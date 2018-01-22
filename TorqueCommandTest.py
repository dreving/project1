from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
import pickle
import copy
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from BrakeController import Controller
import os


'''
Script for executing torque commands with controller model
Used for sawtooth tests and the final tests
'''
# metadata to save for test
brakeID = 1742
breed = 'PendTest'
calTestBreed = 'PG188Test'
DNATestBreed = 'DNATest'
testID = 'MoreTrials_DNARedo5'
test = breed + str(testID)

currdir = 'data/' + str(brakeID) + '/' + breed + \
    '/' + breed + str(testID) + '/'

# name of test from which to extract curve parameters
paramTestID = 2
paramdir = 'data/' + str(brakeID) + '/' + calTestBreed + \
    '/' + calTestBreed + str(paramTestID) + '/'
DNAID = 3
DNAparamdir = 'data/' + str(brakeID) + '/' + DNATestBreed + \
    '/' + DNATestBreed + str(DNAID) + '/'
# (length, width) of plots
figsize = (2000 / 120, 800 / 120)

BBI_TList = [2.14, 4.28, 8.57, 10.71, 15.00, 17.14, 21.42, 25.71, 32.14, 38.56,
             42.85, 47.13, 53.56, 59.99, 64.27, 72.84, 79.27, 85.69, 92.12,
             96.41, 107.12]

BBI_TList = [2.14, 6.427, 10.71, 15.00, 21.42,
             25.71, 29.99, 32.14, 34.28, 38.56, 42.85]
BBI_StepList = [1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
# for sawtooth tests


def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList


# move down to 55% of set value and back up
def exercise(peak, step):
    exer = []
    low = .50 * peak
    numsteps = max(np.ceil((peak - low) / step), 2)
    fall = np.linspace(peak, low, numsteps, endpoint=True)
    fall = np.arange(peak, low, -step)
    exer.extend(fall)
    exer.extend(fall[-2::-1])
    return exer


# list of exercises that move from value to 55% and back up
def workout(exerList, step, rest=False):
    cmds = []
    if type(step) is int:
        step = np.full(len(exerList), step)
    for i in range(len(exerList)):
        cmds.extend(exercise(exerList[i], step[i]))
        if rest:
            cmds.append(0)
    return cmds


if not os.path.exists(currdir):
    os.makedirs(currdir)


# seed random value
np.random.seed(44)

# torqueList will be list of commands
# final tests

# TList_Shuff = copy.deepcopy(BBI_TList)
# np.random.shuffle(TList_Shuff)
TList_Shuff = np.asarray([BBI_TList, BBI_StepList])
np.random.shuffle(TList_Shuff.T)


torqueList = workout(TList_Shuff[0, :], TList_Shuff[1, :])
# sawtooth
# torqueList = pendTorqueList(0,0, 110, 10 )


# makes labels, will get messy
trialTicks = []
for torque in torqueList:
    trialTicks.append(str(torque) + ' in-lb')
trialTicks = tuple(trialTicks)

# Build Model
with open(paramdir + 'curveP.pickle', 'rb') as g:
    (p1, p2) = pickle.load(g)

with open(DNAparamdir + 'DNAP.pickle', 'rb') as g:
    (toFallP, toRiseP, lowerFix, lowerShift, upperFix, upperShift) = pickle.load(g)


cont = Controller(p1, p2,toFallP=toFallP,toRiseP=toRiseP,lowerFix=lowerFix, lowerShift=lowerShift, upperFix = upperFix, upperShift = upperShift)

# run controller over torque commands
brakeStrength, labels = cont.model_DNA(torqueList)

# save log of data
datalog = cont.exportLog()
np.savetxt(currdir + test + 'ControllerLog.csv', datalog, fmt='%.2f',
           delimiter=',', newline='\n', header=('Torque, Command, State'),
           footer='', comments='# ')

# prevent commands below 0% or over 100%
for i in range(len(brakeStrength)):
    brakeStrength[i] = min(max(brakeStrength[i], 0.0), 100.0)

# run test
if not os.path.exists(currdir + test + '.csv'):
    (data, brakeStrength) = collect(brakeStrength, currdir,
                                    test, timeLength=15, mode='warmup',
                                    testSet=2, breed=breed, stepwise=True)
# load results from test
data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')

# analyze results
compData = arrange(data, brakeStrength, currdir, test, )
realTorques = compData[:, -1]
error = realTorques - torqueList

# results plot
fig = plt.figure(figsize=figsize)
ax0 = fig.add_subplot(111)
ax0.scatter(range(len(trialTicks)), realTorques, marker="X")
ax0.scatter(range(len(trialTicks)), torqueList, marker="X")
plt.title('Actual Torque vs Command')
ax0.set_xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
ax0.set_ylabel('Torque (in-lb)')
ax0.legend(('Measured Torque', 'Command'))
plt.tight_layout()
plt.savefig(currdir + test + 'figure1.png')
plt.show()

# error plot
fig = plt.figure(figsize=figsize)
ax1 = fig.add_subplot(211)
ax1.scatter(range(len(trialTicks)), error, marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(in-lb)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
ax1 = fig.add_subplot(212)
ax1.scatter(range(len(trialTicks)), 100 * abs(error) / torqueList, marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(%)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
plt.tight_layout()
plt.savefig(currdir + test + 'figure2.png')
plt.show()

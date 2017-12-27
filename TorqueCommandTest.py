from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from BrakeController import Controller
import os


# List of Torque Commands

breed = 'PendTest'


def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList


testID = 'RandomTorqueSeed44-Avg of Curves'
test = breed + str(testID)
currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
np.random.seed(44)
if not os.path.exists(currdir):
    os.makedirs(currdir)
# torqueList = pendTorqueList(115.0, 110.0, 0.0, -10, 1)
torqueList = np.random.random_integers(0, 1000, 20) / 10.0
print(torqueList)
trialTicks = []
for torque in torqueList:
    trialTicks.append(str(torque) + ' in-lb')
trialTicks = tuple(trialTicks)
# 1 / 0
# Build Model
with open('data/' + 'ControllerI3' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
with open('data/' + 'boundPI3' + '.pickle', 'rb') as g:
    boundP = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL, boundP)

brakeStrength, labels = cont.qmodel_low(torqueList)
for i in range(len(brakeStrength)):
    brakeStrength[i] = min(max(brakeStrength[i], 0.0), 100.0)

# 1/0
# Execute Brake Commands
# What to do about wait time
if not os.path.exists(currdir + test + '.csv'):
    (data, brakeStrength) = collect(brakeStrength, currdir,
                                    test, timeLength=15, mode='warmup', testSet=2, breed=breed,stepwise=True)
data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')
compData = arrange(data, brakeStrength, currdir, test, )
realTorques = compData[:, -1]
error = realTorques - torqueList
fig = plt.figure(figsize=(2000/120, 800/120))
ax0 = fig.add_subplot(111)
# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)
ax0.scatter(range(len(trialTicks)), realTorques,marker="X")
ax0.scatter(range(len(trialTicks)), torqueList,marker="X")
plt.title('Actual Torque vs Command')
ax0.set_xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
ax0.set_ylabel('Torque (in-lb)')
ax0.legend(('Measured Torque', 'Command'))
plt.tight_layout()
plt.savefig(currdir + test + 'figure1.png')
plt.show()
fig = plt.figure(figsize=(2000/120, 800/120))
ax1 = fig.add_subplot(211)
ax1.scatter(range(len(trialTicks)), error,marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(in-lb)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
ax1 = fig.add_subplot(212)
ax1.scatter(range(len(trialTicks)), 100 * abs(error) / torqueList,marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(%)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
plt.tight_layout()
plt.savefig(currdir + test + 'figure2.png')
plt.show()

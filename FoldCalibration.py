from arrangeBrakeData import arrangeBrakeData as arrange
# from mvnaiveanalyze import mvnaiveanalyze as analyze
# from sklearn.svm import SVC
# from naiveanalyze import naiveanalyze as analyze
import pickle
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RiseFallSVM as svm
import simpSVM
# from BrakeModel import BrakeModel
from BrakeController import Controller
from xyFit import *

# function for using parameters found by xfit


def gf(data, *args, **kwargs):
    val = args[0]
    # global xParamLength
    xPL = kwargs.get('xPL', None)
    # print(xPL)
    for i in range(1, len(args)):
        i // xPL
        # coefficients of ascending degree
        val += args[i] * data[int(i >= xPL),

                              :]**(int(i >= xPL) + (i) % xPL)
    return val


def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList


# file saving variables
breed = 'PG188Test'
testIDs = ['CoolDownTest42', 'CoolDownTest43', 'CoolDownTest44', 'CoolDownTest45']
numTests = len(testIDs)
overwrite = False
convert = True

# parameters to tune
C=100000 
gamma=20
boundXL = 4
riseXL = 6
fallXL = 4
riseDXL = 0
fallDXL = 0



# Generate Commands for Tests
# load Placid Data
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.25
Command1 = placidData[:, 0]
actPlacidCommand = placidData[:, 1]
# make previous command column
prevStrength = np.hstack(([0], placidData[:-1, 1]))
placCMD = np.vstack((Command1, prevStrength))

Command2 = pendTorqueList(0.0, 0.0, 120.0, 10, 1)
Command3 = pendTorqueList(115.0, 115.0, 5.0, -10, 1)


# allocate arrays to store control parameters and results of tests
controlPs = np.zeros((numTests, riseXL + riseDXL +
                      fallXL + fallDXL + boundXL + 1))
PlacidResults = np.zeros((numTests, len(Command1)))
TC1Results = np.zeros((numTests, len(Command2)))
TC2Results = np.zeros((numTests, len(Command3)))


for i in range(numTests):
    test = breed + testIDs[i]
    currdir = 'data/' + breed + '/' + breed + str(testIDs[i]) + '/'
    data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
    brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                               test + '.csv', delimiter=',', comments='# ')
    compData = arrange(data, brakeStrength, currdir, test, convert=convert)

# extract atrials and trials from file header
    with open(currdir + test + '.csv', newline='') as csvfile:
        header = next(csv.reader(csvfile, delimiter=',', quotechar='|'))
        header = ''.join(header)
        # import pts and timeLength here
        l = []
        for t in header.split():
            try:
                l.append(float(t))
            except ValueError:
                pass
    if len(l) > 1:
        trials = int(l[0])
        atrials = int(l[1])
    # fig = plt.figure()
    # ax0 = fig.add_subplot(111, projection='3d')
    # ax0.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
    #             c=compData[:, 0] - compData[:, 1], depthshade=False)
    # plt.title('Brake Commands Vs. Torque')
    # ax0.set_xlabel('Brake Command (%)')
    # ax0.set_ylabel(' Prev Brake Command (%)')
    # ax0.set_zlabel('Torque (in-lb)')

    # # Plot Compdata with atrials labeled
    # ax0 = fig.add_subplot(111, projection='3d')
    # ax0.scatter(compData[:trials, 0], compData[:trials, 1],
    #             compData[:trials, 2], c='k', depthshade=False)
    # ax0.scatter(compData[trials:(trials + atrials // 2), 0],
    #             compData[trials:(trials + atrials // 2), 1],
    #             compData[trials:(trials + atrials // 2), 2],
    #             c='r', depthshade=False)
    # ax0.scatter(compData[(trials + atrials // 2):, 0],
    #             compData[(trials + atrials // 2):, 1],
    #             compData[(trials + atrials // 2):, 2],
    #             c='b', depthshade=False)
    # plt.title('Brake Commands Vs. Torque')
    # ax0.set_xlabel('Brake Command (%)')
    # ax0.set_ylabel(' Prev Brake Command (%)')
    # ax0.set_zlabel('Torque (in-lb)')
    
    # plt.savefig(currdir + test + 'figure2.png')
    ncompData = compData[:, (0, 2)]
    # plt.show()

    if atrials > 0:
        rData = ncompData[trials:(trials + atrials // 2), :]
        fData = ncompData[(trials + atrials // 2):, :]

        base = min(rData[:, -1])
        top = max(fData[:, -1])
        # rData = np.vstack((rData, np.tile([0, base], [50, 1])))
        # fData = np.vstack((fData, np.tile([100, top], [500, 1])))
        # TODO add min and max values to increase weight
        clf, scaler = svm.build(rData, fData,C=C, gamma=gamma)
        boundP = simpSVM.simplify(clf, scaler, convert=convert,
                                  boundXL=boundXL)

    labels = svm.qlabel(boundP, ncompData)
    riseData, fallData = svm.split(compData, labels)

    # print(np.shape(riseData))
    fig2 = plt.figure()
    ax0 = fig2.add_subplot(111, )  # projection='3d')
    cmdRange = np.linspace(0.0, 100.0, 100)
    bpts = np.polyval(boundP, cmdRange)
    ax0.scatter(riseData[:, 0], riseData[:, -1],  # riseData[:, 2],
                c='r')
    ax0.scatter(fallData[:, 0], fallData[:, -1],  # fallData[:, 2],
                c='b', )  # depthshade=False)
    ax0.scatter(cmdRange, bpts, c='g')
    plt.title('Brake Commands Vs. Torque')
    ax0.set_xlabel('Brake Command (%)')
    ax0.set_ylabel(' Torque (%)')
    # ax0.set_zlabel('Torque (in-lb)')
    ax0.legend(('Lower Hysteresis Curve', 'Upper Hysteresis Curve', 'Boundary'))
    plt.savefig(currdir + test + 'figure3.png')
    # plt.show()

    # Try single variable analysis for each

    # Add intercepts here
    base = min(riseData[:, -1])
    top = max(fallData[:, -1])

    # points to determine fit #This introduces fake derivative point but
    # points reaching the bottom should be the same anyway...
    rpoints = np.vstack(
        (riseData[:, (0, 1, 2)], np.tile([100, top, top], [25, 1])))
    fpoints = np.vstack(
        (fallData[:, (0, 1, 2)], np.tile([0, base, base], [25, 1])))

    # derivative
    rpoints[:, 1] = rpoints[:, 2] - rpoints[:, 1]
    fpoints[:, 1] = fpoints[:, 2] - fpoints[:, 1]

    # fits

    riseXY = xyFit(riseXL, riseDXL)
    p1 = riseXY.fit(rpoints[:, (2, 1)], rpoints[:, 0])
    fallXY = xyFit(fallXL, fallDXL)
    p2 = fallXY.fit(fpoints[:, (2, 1)], fpoints[:, 0])

    # run function over percentages to get torques

    controlP = np.append(boundP, p1)
    controlP = np.append(controlP, p2)
    controlPs[i, :] = controlP
    cont = Controller(clf, scaler, p1, riseXL, p2, fallXL, boundP)

    theoCMDS1, labels = cont.qmodel(Command1)
    cont.reset()
    theoCMDS2, labels = cont.qmodel(Command2)
    cont.reset()
    theoCMDS3, labels = cont.qmodel(Command3)

    PlacidResults[i, :] = theoCMDS1
    TC1Results[i, :] = theoCMDS2
    TC2Results[i, :] = theoCMDS3

fig = plt.figure()
ax0 = fig.add_subplot(111)
cmdRange = np.linspace(0.0, 100.0, 100)
for i in range(numTests):
    bpts = np.polyval(controlPs[i, :(boundXL + 1)], cmdRange)
    ax0.plot(cmdRange, bpts, '^')
ax0.set_title('Hysteresis Boundaries')
ax0.set_xlabel('Command(%)')
ax0.set_ylabel('Torque(in-lb')
ax0.legend(tuple(testIDs))
plt.show()

fig = plt.figure()
ax0 = fig.add_subplot(311)
ax1 = fig.add_subplot(312)
ax2 = fig.add_subplot(313)
# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)

for i in range(numTests):
    ax0.plot(PlacidResults[i, :])
    ax1.plot(TC1Results[i, :])
    ax2.plot(TC2Results[i, :])
ax0.plot(actPlacidCommand, 'k--')
ax0.set_title('Placid Stepwise Commands')
ax0.set_xlabel('Datapoint')
ax0.set_ylabel('Command(%)')
testIDs.append('Placid Data')
ax0.legend(testIDs)

ax1.set_title('Torque Command: Rising')
ax1.set_xlabel('Datapoint')
ax1.set_ylabel('Command(%)')

ax2.set_title('Torque Command: Falling')
ax2.set_xlabel('Datapoint')
ax2.set_ylabel('Command(%)')


header = 'boundP, ' * (boundXL + 1) + 'riseP, ' * (riseXL) + \
    'riseDeriv, ' * riseDXL + 'fallP, ' * fallXL + 'fallDeriv, ' * fallDXL
np.savetxt('data/ControlPs.csv', controlPs,
           fmt='%.5f', delimiter=',', newline='\n', header=header)


# plt.savefig(currdir + test + 'figure1.png')
plt.show()

from collectBrakeData import collectBrakeData as collect
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


# file saving variables
breed = 'PG188Test'
testID = 'Stress15'
currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
test = breed + str(testID)
overwrite = False
convert = False

# test function parameters
trials = [100, 1000] * 50
atrials = 0


# makes filepath and runs test if it doesn't already exist
if not os.path.exists(currdir):
    os.makedirs(currdir)
if (overwrite or (not os.path.exists(currdir + test + '.csv'))):
    (data, brakeStrength) = collect(trials, currdir, test, atrials=atrials,timeLength=3.0)

# loads data from previous test
data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')


# plot figure 1 here(Raw Data)
time = data[:, 0]
ax = plt.subplot(411)
ax.plot(time,
        data[:, 1],)
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(412)
ax1.plot(time,
         data[:, -2], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(413)
ax2.plot(time,
         data[:, -1])
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')
plt.savefig(currdir + test + 'figure1.png')
# plt.show()


compData = arrange(data, brakeStrength, currdir, test, convert=convert)

# extra atrials and trials from file header
with open(currdir + test + '.csv', newline='') as csvfile:
    header = next(csv.reader(csvfile, delimiter=',', quotechar='|'))
    header = ''.join(header)
    print(header)
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

# Plot Compressed Data
fig = plt.figure()
ax0 = fig.add_subplot(111, projection='3d')
ax0.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
            c=compData[:, 0] - compData[:, 1], depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Prev Brake Command (%)')
ax0.set_zlabel('Torque (in-lb)')

# Plot Compdata with atrials labeled
ax0 = fig.add_subplot(111, projection='3d')
ax0.scatter(compData[:trials, 0], compData[:trials, 1], compData[:trials, 2],
            c='k', depthshade=False)
ax0.scatter(compData[trials:(trials + atrials // 2), 0], compData[trials:(trials + atrials // 2), 1], compData[trials:(trials + atrials // 2), 2],
            c='r', depthshade=False)
ax0.scatter(compData[(trials + atrials // 2):, 0], compData[(trials + atrials // 2):, 1], compData[(trials + atrials // 2):, 2],
            c='b', depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Prev Brake Command (%)')
ax0.set_zlabel('Torque (in-lb)')
ncompData = compData[:, (0, 2)]
plt.savefig(currdir + test + 'figure2.png')
# plt.show()

if atrials > 0:
    rData = ncompData[trials:(trials + atrials // 2), :]
    fData = ncompData[(trials + atrials // 2):, :]

    base = min(rData[:, -1])
    top = max(fData[:, -1])
    # rData = np.vstack((rData, np.tile([0, base], [50, 1])))
    # fData = np.vstack((fData, np.tile([100, top], [500, 1])))
    # TODO add min and max values to increase weight
    clf, scaler = svm.build(rData, fData)
    with open('data/' + 'Controller' + '.pickle', 'wb') as f:
        pickle.dump(clf, f)
    boundP = simpSVM.simplify(clf, scaler, convert=False)


# with open('data/' + 'BackupController' + '.pickle', 'rb') as g:
#     (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
# with open('data/' + 'boundP' + '.pickle', 'rb') as g:
#     boundP = pickle.load(g)
# labels = svm.label(clf, scaler, ncompData)
labels = svm.qlabel(boundP, ncompData)
print(np.shape(labels))
print(np.shape(ncompData))
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
riseXL = 6
fallXL = 6
riseXY = xyFit(riseXL, 0)
p1 = riseXY.fit(rpoints[:, (2, 1)], rpoints[:, 0])
fallXY = xyFit(fallXL, 0)
p2 = fallXY.fit(fpoints[:, (2, 1)], fpoints[:, 0])

# deprecated fit styles
# p1 = np.polyfit(rpoints[:, -1], rpoints[:, 0], 6)
# p2 = np.polyfit(fpoints[:, -1], fpoints[:, 0], 3)
# p1 = np.polyfit(riseData[:, 0], riseData[:, 2], 3)
# p2 = np.polyfit(fallData[:, 0], fallData[:, 2], 2)
# p1 = analyze(riseData[:, (0, 2)], 5, True)
# p2 = analyze(fallData[:, (0, 2)], 5, True)


# print(p)

# load pLacid Data
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.25
actTorque = placidData[:, 0]
Command = placidData[:, 1]
# make previous command column
prevStrength = np.hstack(([0], placidData[:-1, 1]))
placCMD = np.vstack((Command, prevStrength))

# run function over percentages to get torques
# brake = BrakeModel(clf, p1, p2)
# cont = Controller(clf, scaler, p1, riseXL, p2, fallXL)
controlP = (clf, scaler, p1, riseXL, p2, fallXL)
with open('data/' + 'Controller' + '.pickle', 'wb') as f:
    pickle.dump(controlP, f)
# with open('data/' + 'Controller' + '.pickle', 'rb') as g:
#     (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
# with open('data/' + 'boundP' + '.pickle', 'rb') as g:
#     boundP = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL, boundP)

theoCMDS, labels = cont.qmodel(actTorque)

ax = plt.subplot(111)
if convert:
    cmdRange = np.linspace(0, 115, 100)
    rpts = np.polyval(p1[(riseXL - 1)::-1], cmdRange)
    fpts = np.polyval(p2[(fallXL - 1)::-1], cmdRange)
    ax0 = ax.plot(Command, actTorque, 'k--', theoCMDS[:16],
                  actTorque[:16], 'b^', theoCMDS[16:], actTorque[16:], 'g^', rpts, cmdRange, 'r--', fpts, cmdRange, 'b--')  # ,cmdRange,np.polyval(p3,cmdRange),'g--')
    plt.legend(ax0, ('PlacidData', 'Lower Fit', 'Upper Fit',
                     'Lower Polynomial', 'Upper Polynomial'))
    plt.title('Brake Command Vs. Torque')
    plt.ylabel('Torque (in-lb)')
    plt.xlabel('Brake Command (%)')
    plt.savefig(currdir + test + 'figure4.png')

else:
    cmdRange = np.linspace(0, 10, 100)
    rpts = np.polyval(p1[(riseXL - 1)::-1], cmdRange)
    fpts = np.polyval(p2[(fallXL - 1)::-1], cmdRange)
    ax0 = ax.plot(rpts, cmdRange, 'r--', fpts, cmdRange, 'b--')  # ,cmdRange,np.polyval(p3,cmdRange),'g--')
    plt.legend(ax0, (
                     'Lower Polynomial', 'Upper Polynomial'))
    plt.title('Brake Command Vs. Torque')
    plt.ylabel('Torque (in-lb)')
    plt.xlabel('Brake Command (%)')
    plt.savefig(currdir + test + 'figure4.png')
# plt.show()
ranTestdir = 'data/PG188Test/PG188TestRandomTest/'
if os.path.exists(ranTestdir):

    randata = np.loadtxt(ranTestdir + 'PG188TestRandomTest.csv',
                         delimiter=',', comments='# ')
    ranBrakeStrength = np.loadtxt(
        ranTestdir + 'BrakeCommandsPG188TestRandomTest.csv',
        delimiter=',', comments='# ')
    rancompData = np.loadtxt(ranTestdir + 'CompUnconverted' + 'PG188TestRandomTest.csv',
                             delimiter=',', comments='#')

    cont.reset()
    # rancompData = compData
    randTorques = rancompData[:, -1]
    theoRandCMDs, labels = cont.qmodel(randTorques)

    fig2 = plt.figure()
    ax0 = fig2.add_subplot(111, projection='3d')
    # ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
    #             c='b', depthshade=False)
    ax0.scatter(rancompData[:, 2], rancompData[:, 1], theoRandCMDs - rancompData[:, 0],
                c='r')
    plt.title('Brake Commands Vs. Torque')
    ax0.set_xlabel('Torque (in-lb)')
    ax0.set_ylabel(' Prev Torque (in-lb)')
    ax0.set_zlabel('Brake Command Error  (%)')
    # ax0.legend(('Actual CMD', 'Predicted CMD'))
    plt.savefig(currdir + test + 'figure5.png')
    plt.show()

    fig2 = plt.figure()
    ax0 = fig2.add_subplot(111)
    ax0.plot(theoRandCMDs - rancompData[:, 0])
    plt.title('Brake Command Error over Time')
    plt.ylabel('Absolute Error')
    plt.xlabel('Brake Command (%)')
    plt.savefig(currdir + test + 'figure6.png')
    # plt.show()
    theoRandCMDs = np.asarray(theoRandCMDs).T
    theoRandCMDs = theoRandCMDs.reshape(-1, 1)

    result = np.hstack((rancompData, theoRandCMDs))
    np.savetxt(currdir + 'Result' + test + '.csv', result, fmt='%.3f', delimiter=',', newline='\n',
               header='Actual Command, Previous Torque, Measured Torque, Predicted Command', footer='', comments='# ')

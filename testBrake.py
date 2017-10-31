# from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
# from mvnaiveanalyze import mvnaiveanalyze as analyze
# from sklearn.svm import SVC
# from naiveanalyze import naiveanalyze as analyze
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RiseFallSVM as svm
# from BrakeModel import BrakeModel
from BrakeController import Controller
from xyFit import *


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


test = 'PG188Test10.csv'
trials = 100
atrials = 350
pts = 75
(data, BrakeStrength) = collect(trials, test, pts=pts, atrials=atrials)
data = np.loadtxt('data/' + test, delimiter=',', comments='# ')
# for i in range(np.shape(data)[0]):
#         if data[i,4] < 0 or data[i,4] > 11:
#             data[i,4] = np.nan
BrakeStrength = np.loadtxt('data/BrakeCommands' +
                           test, delimiter=',', comments='# ')

time = data[:, 0]
# plot here
ax = plt.subplot(411)
ax.plot(time,
        data[:, 2],)
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(412)
ax1.plot(time,
         data[:, 4], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(413)
ax2.plot(time,
         data[:, 5])
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')

# plt.show()
compData = arrange(data, BrakeStrength, test, pts=pts)
# plt.plot(BrakeStrength)
# plt.show()

# compData = np.loadtxt('data/Comp' + test, delimiter=',', comments='#')
fig = plt.figure()
ax0 = fig.add_subplot(111, projection='3d')
print(np.shape(compData))
ax0.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
            c=compData[:, 0] - compData[:, 1], depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Prev Brake Command (%)')
ax0.set_zlabel('Torque (in-lb)')

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

# ax1 = fig.add_subplot(122, projection='3d')

# ax1.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
#             c=compData[:, 0] - compData[:, 1], depthshade=False)
# plt.title('Brake Commands Vs. Torque')
# ax1.set_xlabel('Brake Command (%)')
# ax1.set_ylabel(' Prev Brake Command (%)')
# ax1.set_zlabel('Torque (in-lb)')
ncompData = compData[:, (0, 2)]
plt.show()
rData = ncompData[trials:(trials + atrials // 2), :]
fData = ncompData[(trials + atrials // 2):, :]

base = min(rData[:, -1])
top = max(fData[:, -1])
rData = np.vstack((rData, np.tile([0, base], [50, 1])))
fData = np.vstack((fData, np.tile([100, top], [500, 1])))
# TODO add min and max values to increase weight
clf, scaler = svm.build(rData, fData)
with open('data/' + 'Controller' + '.pickle', 'wb') as f:
    pickle.dump(clf, f)
with open('data/' + 'Controller' + '.pickle', 'rb') as g:
    clf = pickle.load(g)
labels = svm.label(clf, scaler, ncompData)
riseData, fallData = svm.split(compData, labels)


# print(np.shape(riseData))
fig2 = plt.figure()
ax0 = fig2.add_subplot(111, )  # projection='3d')
ax0.scatter(riseData[:, 0], riseData[:, -1],  # riseData[:, 2],
            c='r')
ax0.scatter(fallData[:, 0], fallData[:, -1],  # fallData[:, 2],
            c='b', )  # depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Torque (%)')
# ax0.set_zlabel('Torque (in-lb)')
ax0.legend(('Lower Hysteresis Curve', 'Upper Hysteresis Curve'))
plt.show()


# Try single variable analysis for each

# p = analyze(compData, 5, True)
# p0 = clf.get_params()
# Add intercepts here
base = min(riseData[:, -1])
top = max(fallData[:, -1])

# print(np.tile([100, top], [10,1]))
rpoints = np.vstack(
    (riseData[:, (0, 1, 2)], np.tile([100, top, top], [25, 1])))
fpoints = np.vstack(
    (fallData[:, (0, 1, 2)], np.tile([0, base, base], [25, 1])))
# for brake
# p1 = np.polyfit(rpoints[:, 0], rpoints[:, 1], 4)
# p2 = np.polyfit(fpoints[:, 0], fpoints[:, 1], 3)
# derivative
rpoints[:, 1] = rpoints[:, 2] - rpoints[:, 1]
fpoints[:, 1] = fpoints[:, 2] - fpoints[:, 1]
# for
riseXL = 6
fallXL = 6
riseXY = xyFit(riseXL, 4)
print(rpoints)
p1 = riseXY.fit(rpoints[:, (2, 1)], rpoints[:, 0])
print(p1)
fallXY = xyFit(fallXL, 4)
p2 = fallXY.fit(fpoints[:, (2, 1)], fpoints[:, 0])
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
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL)
controlP = (clf, scaler, p1, riseXL, p2, fallXL)
with open('data/' + 'Controller' + '.pickle', 'wb') as f:
    pickle.dump(controlP, f)
with open('data/' + 'Controller' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL)
# print(clf.coef_)
# c = clf.coef_
# c = c[0]
# y = clf.intercept_
# p3 = [-c[0] / c[1], -y/c[1]]
# theoTorques, labels = brake.model(Command)
theoCMDS, labels = cont.model(actTorque)
print(theoCMDS)
print(labels)
# theoTorques = gf(placCMD, *(p[0]), xPL=p[2])

# print(np.shape(theoTorques))
# plot over data
# run function over percentages to get torques
ax = plt.subplot(111)
# ax0 = ax.plot(Command, actTorque, 'k--', Command[:16],
#               theoTorques[:16], 'b^', Command[16:], theoTorques[16:], 'g^')

cmdRange = np.linspace(0, 115, 100)
# rpts = np.polyval(p1, cmdRange)
# fpts = np.polyval(p2, cmdRange)
ax0 = ax.plot(Command, actTorque, 'k--', theoCMDS[:16],
              actTorque[:16], 'b^', theoCMDS[16:], actTorque[16:], 'g^',) # rpts, cmdRange, 'r--', fpts, cmdRange, 'b--')  # ,cmdRange,np.polyval(p3,cmdRange),'g--')
plt.legend(ax0, ('PlacidData', 'Lower Fit', 'Upper Fit',
                 'Lower Polynomial', 'Upper Polynomial'))
plt.title('Brake Command Vs. Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')

# flipped
# ax0 = ax.plot(actTorque, Command, 'k--',
#               actTorque[:16], theoCMDS[:16], 'b^', actTorque[16:], theoCMDS[16:], 'g^')
# plt.legend(ax0, ('PlacidData', 'Lower Fit', 'Upper Fit'))
# plt.title('Brake Command Vs. Torque')
# plt.xlabel('Torque (in-lb)')
# plt.ylabel('Brake Command (%)')

# ax = plt.subplot(122)
# print(np.shape(placidData[:, 0]))
# currError = (theoTorques - actTorque)
# ax1 = ax.plot(Command[:16], currError[:16], 'r^',
#               Command[16:], currError[16:], 'y^')
# plt.title('Brake Command Vs. Error')
# plt.legend(ax0, ('Lower Fit', 'Upper Fit'))
# plt.ylabel('Torque (in-lb)')
# plt.xlabel('Brake Command (%)')

plt.show()


randata = np.loadtxt('data/RandomTest.csv', delimiter=',', comments='# ')
# for i in range(np.shape(data)[0]):
#         if data[i,4] < 0 or data[i,4] > 11:
#             data[i,4] = np.nan
ranBrakeStrength = np.loadtxt(
    'data/BrakeCommandsRandomTest.csv', delimiter=',', comments='# ')
# rancompData = arrange(randata, ranBrakeStrength, 'RandomTest.csv')
# # plt.plot(BrakeStrength)
# # plt.show()

rancompData = np.loadtxt('data/CompRandomTest.csv',
                         delimiter=',', comments='#')

cont.reset()
rancompData = compData
randTorques = rancompData[:, 2]
theoRandCMDs, labels = cont.model(randTorques)

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
plt.show()

fig2 = plt.figure()
ax0 = fig2.add_subplot(111)
ax0.plot(theoRandCMDs - rancompData[:, 0])
plt.title('Brake Command Error over Time')
plt.ylabel('Absolute Error')
plt.xlabel('Brake Command (%)')
plt.show()
theoRandCMDs = np.asarray(theoRandCMDs).T
print(np.shape(rancompData))
theoRandCMDs= theoRandCMDs.reshape(-1,1)
print(np.shape(theoRandCMDs))

result = np.hstack(( rancompData,theoRandCMDs))
np.savetxt('data/Result' + test, result,fmt='%.3f', delimiter=',', newline='\n',
               header='Actual Command, Previous Torque, Measured Torque, Predicted Command', footer='', comments='# ')

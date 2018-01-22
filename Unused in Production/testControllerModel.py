from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RiseFallSVM as svm
from BrakeController import Controller
from xyFit import *


test = 'PG188Test9.csv'
trials = 100
atrials = 350
(data, BrakeStrength) = collect(trials, test, atrials=atrials)
data = np.loadtxt('data/' + test, delimiter=',', comments='# ')
BrakeStrength = np.loadtxt('data/BrakeCommands' +
                           test, delimiter=',', comments='# ')


compData = arrange(data, BrakeStrength, test)
# plt.plot(BrakeStrength)
# plt.show()

# compData = np.loadtxt('data/Comp' + test, delimiter=',', comments='#')
# fig = plt.figure()
# ax0 = fig.add_subplot(111, projection='3d')
# print(np.shape(compData))
# ax0.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
#             c=compData[:, 0] - compData[:, 1], depthshade=False)
# plt.title('Brake Commands Vs. Torque')
# ax0.set_xlabel('Brake Command (%)')
# ax0.set_ylabel(' Prev Brake Command (%)')
# ax0.set_zlabel('Torque (in-lb)')

# ax0 = fig.add_subplot(111, projection='3d')

# ax0.scatter(compData[:trials, 0], compData[:trials, 1], compData[:trials, 2],
#             c='k', depthshade=False)
# ax0.scatter(compData[trials:(trials + atrials // 2), 0], compData[trials:(trials + atrials // 2), 1], compData[trials:(trials + atrials // 2), 2],
#             c='r', depthshade=False)
# ax0.scatter(compData[(trials + atrials // 2):, 0], compData[(trials + atrials // 2):, 1], compData[(trials + atrials // 2):, 2],
#             c='b', depthshade=False)
# plt.title('Brake Commands Vs. Torque')
# ax0.set_xlabel('Brake Command (%)')
# ax0.set_ylabel(' Prev Brake Command (%)')
# ax0.set_zlabel('Torque (in-lb)')

# ax1 = fig.add_subplot(122, projection='3d')

# ax1.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
#             c=compData[:, 0] - compData[:, 1], depthshade=False)
# plt.title('Brake Commands Vs. Torque')
# ax1.set_xlabel('Brake Command (%)')
# ax1.set_ylabel(' Prev Brake Command (%)')
# ax1.set_zlabel('Torque (in-lb)')

# plt.show()

with open('data/' + 'Controller' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)


# run function over percentages to get torques
# brake = BrakeModel(clf, p1, p2)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL)


randata = np.loadtxt('data/' + test, delimiter=',', comments='# ')
# for i in range(np.shape(data)[0]):
#         if data[i,4] < 0 or data[i,4] > 11:
#             data[i,4] = np.nan
ranBrakeStrength = np.loadtxt(
    'data/BrakeCommands' + test, delimiter=',', comments='# ')
rancompData = arrange(randata, ranBrakeStrength, 'RandomTest.csv')
# # plt.plot(BrakeStrength)
# # plt.show()

rancompData = np.loadtxt('data/Comp' + test,
                         delimiter=',', comments='#')

# cont.reset()
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
theoRandCMDs = theoRandCMDs.reshape(-1, 1)


result = np.hstack((rancompData, theoRandCMDs))
np.savetxt('data/Result' + test, result, fmt='%.3f', delimiter=',', newline='\n',
           header='Actual Command, Previous Torque, Measured Torque, Predicted Command', footer='', comments='# ')

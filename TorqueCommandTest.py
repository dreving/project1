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


testID = 11
test = breed + str(testID)
currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
if not os.path.exists(currdir):
    os.makedirs(currdir)
torqueList = pendTorqueList(0.0, 0.0, 110.0, 30, 1)
print(torqueList)
# 1 / 0
# Build Model
with open('data/' + 'BackupController' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
with open('data/' + 'boundP' + '.pickle', 'rb') as g:
    boundP = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL, boundP)
# print(riseXL)
# print(p1[5::-1])
# p3 = p1[-1:5:-1]
# p3 = np.append(p3,0)
# print(p3)
# print(np.polyval(p1[5::-1],74)+np.polyval(p3,74))
# Convert to Brake Commands
# print(cont.model([74.0]))
brakeStrength, labels = cont.qmodel(torqueList)
for i in range(len(brakeStrength)):
    brakeStrength[i] = min(max(brakeStrength[i], 0.0), 100.0)

print(brakeStrength)
# 1/0
# Execute Brake Commands
# What to do about wait time
(data, brakeStrength) = collect(brakeStrength, currdir, test)
compData = arrange(data, brakeStrength, currdir, test)
realTorques = compData[:, -1]
error = torqueList - realTorques
fig = plt.figure()
ax0 = fig.add_subplot(211)
# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)
ax0.plot(realTorques)
ax0.plot(torqueList)
plt.title('Actual Torque vs Command')
ax0.set_xlabel('Datapoint')
ax0.set_ylabel('Torque (in-lb)')
ax0.legend(('Measured Torque', 'Command'))

ax1 = fig.add_subplot(212)
ax1.plot(error)
plt.title('Error of Torque Command')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Datapoint')
plt.savefig(currdir + test + 'figure1.png')
plt.show()

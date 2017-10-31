import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw
import brake
import time
from arrangeBrakeData import arrangeBrakeData as arrange
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RiseFallSVM as svm
from BrakeController import Controller
from xyFit import *

# List of Torque Commands


def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList

fname = 'PendTest5.csv'
torqueList = pendTorqueList(115.0,110.0, 0.0, -10, 5)
print(torqueList)
# 1 / 0
# Build Model
with open('data/' + 'BackupController' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL)
# print(riseXL)
# print(p1[5::-1])
# p3 = p1[-1:5:-1]
# p3 = np.append(p3,0)
# print(p3)
# print(np.polyval(p1[5::-1],74)+np.polyval(p3,74))
# Convert to Brake Commands
# print(cont.model([74.0]))
brakeStrength,labels = cont.model(torqueList)
for i in range(len(brakeStrength)):
    brakeStrength[i] = min(max(brakeStrength[i], 0.0), 100.0)

print(brakeStrength)
# 1/0
# Execute Brake Commands
# What to do about wait time
currentScale = 1000 / 100
motorSpeed = 5  # [20, 20, 20, 20, 20]
timeLength = 5
pts = 75
fullTime = timeLength * len(brakeStrength)

rc = RoboClaw('COM11', 0x80)
Nb, Mc = brake.initNebula()

dt = 1.0 / pts
P = 7
D = 15
I = .1


# initialize Data
# data = np.full([int(fullTime * pts), 6], np.nan)
data = np.full([1, 6], np.nan)
compData = np.full([len(brakeStrength), 3], np.nan)
# Main Loop
# set it to collect data set from one pair of points and then sleep for some amount of time
for point in range(0, len(brakeStrength), 2):
    datapoint = np.full([int(timeLength * 2 * pts), 6], np.nan)
    CMF.setMotorSpeed(rc, motorSpeed)
    time.sleep(1)
    start = time.time()
    currTime = 0.0
    intError = 0
    lastError = 0
    while currTime < (timeLength*2):
        setSpeed = motorSpeed  # [int(np.floor(currTime / timeLength))]
        acSpeed = CMF.readAcSpeed(rc)
        error = setSpeed - acSpeed
        derror = error - lastError
        intError += error
        command = P * error + D * derror + I * intError
        CMF.setMotorSpeed(rc, command)
        lastError = error
        brakeTorque = int(round(
            currentScale * brakeStrength[point:(point + 2)][int(np.floor(currTime / timeLength))]))
        brake.setTorque(Mc, brakeTorque)

        # Record Data here

        # TimeStamp
        datapoint[int(np.floor(currTime / dt)),
             0] = currTime + point * timeLength * 2

        # Brake Command
        datapoint[int(np.floor(currTime / dt)),
             1] = brakeStrength[point:(point + 2)][int(np.floor(currTime / timeLength))]

        # Actual Brake Output
        datapoint[int(np.floor(currTime / dt)),
             2] = brake.readCurrent(Mc) / currentScale
        # prev Brake command
        # if (currTime > timeLength):
        #     data[int(np.floor(currTime - timeLength / dt)),
        #          3] = brakeStrength[int(np.floor(currTime / timeLength))]
        # else:
        #     data[int(np.floor(currTime - timeLength / dt)),
        #          3] = 0
        # Motor Current
        datapoint[int(np.floor(currTime / dt)), 4] = CMF.readInCurrent(rc)

        # Motor Speed
        datapoint[int(np.floor(currTime / dt)), 5] = acSpeed
        # data[int(np.floor(currTime / dt)), 3] = setSpeed
        loopTime = time.time() - currTime - start
        if loopTime < dt:
            time.sleep(dt - loopTime)
        currTime = time.time() - start

    CMF.stopMotor(rc)
    # print('motor Stopped')

    # np.savetxt('data/' + fname, data, fmt='%.2f', delimiter=',', newline='\n',
    #            header='Time, setPoint, Actual Brake Current, prevsetPoint, MotorCurrent' 'MotorSpeed', footer='', comments='# ')
    # np.savetxt('data/BrakeCommands' + fname, brakeStrength, fmt='%.1f', delimiter=',', newline='\n',
    #            header='', footer='', comments='# ')
    brake.setTorque(Mc, 1000)
    # print('brake command sent')
    # brake.close(Nb, Mc)
    # print('brake closed')
    compDP= arrange(datapoint,brakeStrength[point:(point+2)],None,timeLength, pts)
    compData[point:(point+2),:] = compDP
    data= np.vstack((data,datapoint))
    np.savetxt('data/' + fname, data, fmt='%.2f', delimiter=',', newline='\n',
               header='Time, setPoint, Actual Brake Current, prevsetPoint, MotorCurrent' 'MotorSpeed', footer='', comments='# ')
    np.savetxt('data/Comp' + fname, compData, fmt='%.2f', delimiter=',', newline='\n',
               header='setPoint, prevTorque, Torque', footer='', comments='# ')
    time.sleep(timeLength*4)
# compData = arrange(data, BrakeStrength, test)
brake.setTorque(Mc, 0)
brake.close(Nb, Mc)
print('brake closed')
realTorques = compData[:,-1]
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
plt.show()

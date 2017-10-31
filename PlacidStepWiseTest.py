import time
import numpy as np
import matplotlib.pyplot as plt
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
import brake

timeLength = 3.0  # seconds
pts = 75
runs = 3
pause = 40
brakeStrength = [0, 6.8, 13.6, 20.4, 27.2, 34, 40.8, 47.6, 54.4, 62.1, 69.9, 77.7, 85.4, 92.2,
                 99.4, 100, 99.4, 92.2, 85.4, 77.7, 69.9, 62.1, 54.4, 47.6, 40.8, 34, 27.2, 20.4, 13.6, 6.8, 0]
brakeStrength = brakeStrength * runs            
#brakeStrength = [0, 100, 0]
currentScale = 1000 / 100
motorSpeed = 7.5  # [20, 20, 20, 20, 20]
fullTime = timeLength * len(brakeStrength)
rc = RoboClaw('COM11', 0x80)
Nb, Mc = brake.initNebula()
dt = 1.0 / pts
P = 7
D = 15
I = .1
# P = 0
# D = 0
# I = 0
# Create List of Commands
data = np.full([int(fullTime * pts), 5], np.nan)
for point in range(0, len(brakeStrength)):
    intError = 0
    lastError = 0
    # initialize Data
    

    # Main Loop

    CMF.setMotorSpeed(rc, motorSpeed*2)
    time.sleep(1)
    stepTime = 0.0
    currTime = stepTime + timeLength*point
    start = time.time()
    while stepTime < timeLength:
        setSpeed = motorSpeed  # [int(np.floor(currTime / timeLength))]
        acSpeed = CMF.readAcSpeed(rc)
        error = setSpeed - acSpeed
        derror = error - lastError
        intError += error
        command = P * error + D * derror + I * intError
        CMF.setMotorSpeed(rc, command)
        lastError = error
        brakeTorque = round(
            currentScale * brakeStrength[int(np.floor(currTime / timeLength))])
        brake.setTorque(Mc, brakeTorque)

        # Record Data here

        # TimeStamp
        data[int(np.floor(currTime / dt)),
             0] = currTime

        # Brake Command
        data[int(np.floor(currTime / dt)),
             1] = brakeStrength[int(np.floor(currTime / timeLength))]

        # Actual Brake Reading
        data[int(np.floor(currTime / dt)),
             2] = brake.readCurrent(Mc) / currentScale

        # Motor Current
        data[int(np.floor(currTime / dt)), 3] = CMF.readInCurrent(rc)

        # Motor Speed
        data[int(np.floor(currTime / dt)), 4] = acSpeed
        # data[int(np.floor(currTime / dt)), 3] = setSpeed
        loopTime = time.time() - stepTime - start
        if loopTime < dt:
            time.sleep(dt - loopTime)
        stepTime = time.time() - start
        currTime =stepTime + timeLength * point
    CMF.stopMotor(rc)
    time.sleep(pause * brakeStrength[point]/100.0)


CMF.stopMotor(rc)
fname = 'data/PG188PlacidStepwiseTest12.csv'
np.savetxt(fname, data, fmt='%.2f', delimiter=',', newline='\n',
           header='TimeStamp (s), BrakeCommand (%), Actual Brake Torque (%), Motor Current (A), Motor Speed (%)', footer='', comments='# ')

brake.setTorque(Mc, 0)
brake.close(Nb, Mc)

# plot here
ax = plt.subplot(311)
ax.plot(np.linspace(0, fullTime, int(fullTime * pts)),
        data[:, 2],)
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(312)
ax1.plot(np.linspace(0, fullTime, int(fullTime * pts)),
         data[:, 3], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(313)
ax2.plot(np.linspace(0, fullTime, int(fullTime * pts)),
         data[:, 4], label='Motor Current')
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')
plt.show()

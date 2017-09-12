import time
import numpy as np
import matplotlib.pyplot as plt
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
import brake

timeLength = 3.0  # seconds
pts = 100
brakeStrength = [0, 250, 500, 750, 1000]
motorSpeed = [20, 20, 20, 20, 20]
fullTime = timeLength * len(brakeStrength)
rc = RoboClaw('COM10', 0x80)
Nb, Mc = brake.initNebula()
dt = 1.0 / pts
P = 12
D= 4
I =1
# Create List of Commands
intError = 0
lastError = 0
# initialize Data
data = np.full([int(fullTime * pts), 4], np.nan)

# Main Loop

CMF.setMotorSpeed(rc, motorSpeed[0])
time.sleep(1)
start = time.time()
currTime = 0.0
while currTime < fullTime:
    setSpeed = motorSpeed[int(np.floor(currTime / timeLength))]
    acSpeed = CMF.readAcSpeed(rc)
    error = setSpeed - acSpeed
    derror = error - lastError
    intError += error
    command = acSpeed + P * error + D * derror + I * intError
    CMF.setMotorSpeed(rc, command )
    lastError = error
    brakeTorque = brakeStrength[int(np.floor(currTime / timeLength))]
    brake.setTorque(Mc, brakeTorque)
    data[int(np.floor(currTime / dt)),0] = brakeTorque / 10
    data[int(np.floor(currTime / dt)),1] = CMF.readInCurrent(rc)
    data[int(np.floor(currTime / dt)),2] = acSpeed
    data[int(np.floor(currTime / dt)),3] = setSpeed
    loopTime = time.time() - currTime - start
    if loopTime < dt:
        time.sleep(dt - loopTime)
    currTime = time.time() - start


CMF.stopMotor(rc)
brake.setTorque(Mc, 0)
brake.close(Nb, Mc)

# plot here
ax = plt.subplot(311)
ax.plot(np.linspace(0,fullTime,int(fullTime * pts)), data[:, 0], label='Motor Current')
plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(312)
ax1.plot(np.linspace(0,fullTime,int(fullTime * pts)), data[:, 1], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(313)
ax2.plot(np.linspace(0,fullTime,int(fullTime * pts)), data[:, 2], label='Motor Current')
plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')
plt.show()

"""
Set Brake to Nominal Value
Set Motor to Steady State Speed
Wait unti motor hits constant speed
record current for X seconds
Calculate Variance of Current
Increment Speed by S rpm and repeat
Increment Brake Strength by Y% and repeat
Plot: X = speed Y = Variance
Different colors for different Strengths"""
import time
import numpy as np
import matplotlib.pyplot as plt
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
import brake

timeLength = 2.0  # seconds
pts = 100
brakeStrength = [25, 50, 75]
motorSpeed = range(20, 90, 10)
data = np.full([len(motorSpeed), len(brakeStrength)], np.nan)
Nb = brake.initNebula()
rc = RoboClaw('COM7', 0x80)
# Nb = brake.initNebula()
time.sleep(1)

for strength in range(len(brakeStrength)):
    brake.setTorque(Nb, brakeStrength[strength])
    for speed in range(len(motorSpeed)):
        print(motorSpeed[speed])
        CMF.setMotorSpeed(rc, motorSpeed[speed])
        # wait until Steady state confirmed
        # for t in range(pts):
        # figure out real arrangement, maybe a class
        avg, v = CMF.readAvgCurrent(rc, timeLength, pts)
        data[speed, strength] = v
        # time.sleep(timeLength / pts)  #built into function

# Turn off the danger, it's time for science

CMF.stopMotor(rc)
brake.setTorque(Nb, 0)
# analyze all variances here JK Built in Function
# varArray = np.zeros([len(motorSpeed), len(brakeStrength)])
# for strength in range(len(brakeStrength)):
#     for speed in range(len(motorSpeed)):
#         test = data[speed, strength, :]
#         varArray = np.nanvar(test)  # hashtagstats


# plot here
ax = plt.subplot(111)
for strength in range(len(brakeStrength)):
    ax.plot(motorSpeed, data[:, strength])
plt.title('Motor Speed Vs. Variance')
plt.ylabel('Variance')
plt.xlabel('Speed')
plt.show()

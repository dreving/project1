import numpy as np
import brake
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw
from ard_T import Ard_T
import time
import matplotlib.pyplot as plt


def motorModel(speed, torque):
        # Warning on tested for speed 5
    # pwm = 0.0004 * (torque ** 2) + 0.0965 * torque + 1.666 + speed
    pwm = 0.0011 * (torque **2) + 0.0318 * torque + speed
    # B = 1.16
    # M = .1404
    # pwm = speed + B + M * torque
    return pwm


# Initialize everything
print('Initializing')
tc = Ard_T('COM3', 1)
rc = RoboClaw('COM11', 0x80)
Nb, Mc = brake.initNebula()


# desiredSpeed = 40
# guess = 52


# # Set Brake Torque
# brake.setTorque(Mc, 1000)
# # Slight Delay
# time.sleep(.25)
# # Turn On Motor Guess of Appropriate Speed
# CMF.setMotorSpeed(rc, guess)
# # Wait to Speed Up
# time.sleep(2)
# # Read Speed
# speed = CMF.readAcSpeed(rc)
# pw = CMF.readSafeSpeed(rc)
# # Stop Motor
# CMF.stopMotor(rc)
# # Turn Off Brake
# brake.setTorque(Mc, 0)
# print('brake command sent')
# brake.close(Nb, Mc)
# print('brake closed')
# print(speed)

# commented out full test for 0 25 50 75 100 50 0 50 100 0 100 0

torqueList = [0, 25, 50, 75, 100, 50, 0]
speedList = []
for torque in torqueList:
    guess = motorModel(40, torque)
    CMF.setMotorSpeed(rc, guess)
    brake.setTorque(Mc, torque * 10)
# Wait to Speed Up
    time.sleep(2)
    # Read Speed
    speedList.append(CMF.readAcSpeed(rc))
# Stop Motor
CMF.stopMotor(rc)
brake.setTorque(Mc, 0)
print('brake command sent')
brake.close(Nb, Mc)
print('brake closed')
print(speedList)

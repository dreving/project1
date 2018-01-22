import numpy as np
import time
from roboclaw import RoboClaw

'''
CalbrationMotorFunctions.py
Super class for unofficial roboclaw library
class for running the motor on the calibration system

Initialization
rc = CMF(port)
where port is a string where roboclaw can be found, like 'COM5'
'''


class CMF(RoboClaw):
    def __init__(self, port, address=0x80):
        super().__init__(port, address)

    # general function for commannding pwm
    def setMotorSpeed(self, speedPercent):
            # 40RPM Max for continuous
        speedPercent = max(speedPercent, 0)
        speed = min(63, int(speedPercent / 100 * 63))
        self.drive_motor(1, speed)
        # assert -64 <= speed <= 63

    # command feed forward pwm based on expected torque
    def setFFSpeed(self, speedPercent, torque):
        pwm = self.compPWM(speedPercent, torque)
        self.setMotorSpeed(pwm)

    # limits accel and deccel to prevent overcurrent
    # shut off when stopping motor
    def setSafeMotorSpeed(self, speedPercent):
            # 40RPM Max for continuous
        startSpeed = int(self.readPWM())
        if startSpeed > speedPercent:
            accel = -10
        else:
            accel = 10
        for speed in range(startSpeed, speedPercent, accel):
            self.drive_motor(1, int(speed / 100 * 63))
            time.sleep(.1)
        speed = int(speedPercent / 100 * 63)
        self.drive_motor(1, speed)
        time.sleep(.2)
        # assert -64 <= speed <= 63

    # read commanded pwm
    def readPWM(self):
        return self.read_motor_pwm(1)

    # read encoder
    def readAcSpeed(self):
        return max(self.read_speed(1), 0)

    def stopMotor(self):
        self.setSafeMotorSpeed(0)
        time.sleep(.1)
        self.stop_all()

    # instantaneous current reading
    def readInCurrent(self):
        return self.read_motor_current(1)

    # average reading
    def readAvgCurrent(self, secs, rate=100):
        numpts = int(secs * rate)
        wait = 1.0 / rate
        data = np.zeros(numpts)
        for i in range(numpts):
            data[i] = self.readInCurrent()
            time.sleep(wait)
        avg = np.nanmean(data)
        var = np.nanvar(data)
        return (avg, var)

    @staticmethod
    # empirical feed forward pwm calculations for
    # commanding motor speed under expected torque
    def compPWM(speed, torque):
        if speed <= 5:
            pwm = 0.0004 * (torque ** 2) + 0.0965 * \
                torque + 1.666 + speed  # for 5
        else:
            pwm = 0.0011 * (torque ** 2) + 0.0318 * torque + speed
        return pwm

    @staticmethod
    # conversion from current to torque
    def itoT(i, p0=-93.1, p1=67.94, p2=1.297):
        T = p0 + p1 * np.sqrt(i + p2)
        return T

# test code
# motor = CMF('COM7')
# motor.setFFSpeed(40, 0)
# time.sleep(1)
# motor.setFFSpeed(40, 50)
# time.sleep(1)
# print(motor.readPWM())
# print(motor.readAcSpeed())
# print(motor.readInCurrent())
# print(motor.readAvgCurrent(2))
# motor.stopMotor()
# print(CMF.itoT(8))

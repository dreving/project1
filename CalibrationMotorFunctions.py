import numpy as np
import time


def setMotorSpeed(rc, speedPercent):
        # 40RPM Max for continuous
    speedPercent = max(speedPercent, 0)
    speed = min(63, int(speedPercent / 100 * 63))
    rc.drive_motor(1, speed)

    # assert -64 <= speed <= 63


def setSafeMotorSpeed(rc, speedPercent):
        # 40RPM Max for continuous
    startSpeed = int(readSafeSpeed(rc))
    if startSpeed > speedPercent:
        accel = -10
    else:
        accel = 10
    for speed in range(startSpeed, speedPercent, accel):
        rc.drive_motor(1, int(speed / 100 * 63))
        time.sleep(.1)
    # speedPercent /= 1
    # max_speed = rc.read_max_speed(1)
    # speed = round((speedPercent / 100.) * max_speed)
    # rc.set_speed(1, speed)
    # actSpeedPercent = rc.read_speed(1)
    # while abs(actSpeedPercent - speedPercent) > 3:
    #     # print(actSpeedPercent)
    #     actSpeedPercent = rc.read_speed(1)
    #     time.sleep(0.01)
    speed = int(speedPercent / 100 * 63)
    rc.drive_motor(1, speed)
    time.sleep(.2)
    # assert -64 <= speed <= 63


def readSafeSpeed(rc):
    return rc.read_motor_pwm(1)


def readAcSpeed(rc):
    return max(rc.read_speed(1), 0)


def stopMotor(rc):
    setSafeMotorSpeed(rc, 0)
    time.sleep(.1)
    rc.stop_all()


def readInCurrent(rc):
    return rc.read_motor_current(1)


def readAvgCurrent(rc, secs, rate=100):
    numpts = int(secs * rate)
    wait = 1.0 / rate
    data = np.zeros(numpts)
    for i in range(numpts):
        data[i] = readInCurrent(rc)
        time.sleep(wait)
    print(max(data))
    avg = np.nanmean(data)
    var = np.nanvar(data)
    return (avg, var)


def compPWM(speed, torque):
    if speed == 5:
        pwm = 0.0004 * (torque ** 2) + 0.0965 * torque + 1.666 + speed #for 5
    else:
        pwm = 0.0011 * (torque **2) + 0.0318 * torque + speed
    # B = 1.16
    # M = .1404
    # pwm = speed + B + M * torque
    return pwm


def itoT(i):
    # T = -92.74 + 0.0111 * np.sqrt(35872000 * i + 34699500)
    # T = -93.1563 + 0.00965487 * np.sqrt(46320000 * i + 56800000) # for motor speed 10
    T = -120.941 + 0.0111358 * \
        np.sqrt(40160000 * i + 90000000)  # for motor speed 5
    # T = -114.436 + 0.025641 * np.sqrt(7.8e6 * i + 1.52571e7) # For Motor Speed 5 30 second Rest
    # T = -132.179 + 0.079*np.sqrt(895000* i + 2.19199e6)
    return T

import numpy as np
import time


def setMotorSpeed(rc, speedPercent):
        # 40RPM Max for continuous
    max_speed = rc.read_max_speed(1)
    speed = round((speedPercent / 100.) * max_speed)
    rc.set_speed(1, speed)


def stopMotor(rc):
    setMotorSpeed(rc, 0)
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
    avg = np.nanmean(data)
    var = np.nanvar(data)
    return (avg, var)

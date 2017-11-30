import CalibrationMotorFunctions as CMF
import time
from roboclaw import RoboClaw


def warmup(runtime=1200):
    rc = RoboClaw('COM11', 0x80)
    CMF.setMotorSpeed(rc, 5)
    time.sleep(runtime)
    CMF.stopMotor(rc)
    print('Warmup Script Complete')


warmup()

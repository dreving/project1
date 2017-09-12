import numpy as np
import brake
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw


def collectBrakeData(trials, timeLength=3, pts=100):
    """ For Specified number trials
collect information in data
data = trialsx3 array
of columns input voltage, current, label
"""

    rc = RoboClaw('COM10', 0x80)
    Nb = brake.initNebula()
# imports and set ups
    data = np.zeros(trials, 3)
    motorSpeedList = [50]
    maxTorque = 100.0
    data[0, 2] = 0
    brake.setTorque(Nb, strength)
    CMF.setMotorSpeed(motorSpeedList[0])
    noLoadCurrent = CMF.readAvgCurrent(rc, timeLength, pts)
    for t in range(trials):
        # Input random voltage for torque
        strength = np.random.randint(0, 1001)
        data[t, 0] = strength
        brake.setTorque(Nb, strength)

    # Set motor Speed based on estimate to reduce variance
        CMF.setMotorSpeed(motorSpeedList[np.floor(
            brake / maxTorque * len(motorSpeedList))])
    # Read value current I from controller
        I, v = CMF.readAvgCurrent(rc, timeLength, pts)
    # Do Interpolation to calculate Torque
        data[t, 1] = np.nan  # TODO math
        # Make Array of Input voltage and corresponding torque
    # Label Data based on if previous value was
        if t > 0:
            data[t, 2] = data[t - 1, 1]
    # less than (0) or greater than (1) new value
    # First value is always zero

    CMF.stopMotor(rc)
    brake.setTorque(Nb, 0)
    fname = 
    np.savetxt(fname, data, fmt='%.2f', delimiter=',', newline='\n', header='setPoint, prevsetPoint, Current', footer='', comments='# ')
    n
    return data

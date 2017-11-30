import numpy as np
import brake
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw
import time
import matplotlib.pyplot as plt


def collectBrakeData(trials, currdir, fname, timeLength=3, pts=150, atrials=0):
    """ For Specified number trials
collect information in data 
data = trialsx3 array
of columns input voltage, current, label
"""

#     rc = RoboClaw('COM10', 0x80)
#     Nb = brake.initNebula()
# # imports and set ups
#     data = np.zeros(trials, 3)
#     motorSpeedList = [50]
#     maxTorque = 100.0
#     data[0, 2] = 0
#     brake.setTorque(Nb, strength)
#     CMF.setMotorSpeed(motorSpeedList[0])
#     noLoadCurrent = CMF.readAvgCurrent(rc, timeLength, pts)
#     for t in range(trials):
#         # Input random voltage for torque
#         strength = np.random.randint(0, 1001)
#         data[t, 0] = strength
#         brake.setTorque(Nb, strength)

#     # Set motor Speed based on estimate to reduce variance
#         CMF.setMotorSpeed(motorSpeedList[np.floor(
#             brake / maxTorque * len(motorSpeedList))])
#     # Read value current I from controller
#         I, v = CMF.readAvgCurrent(rc, timeLength, pts)
#     # Do Interpolation to calculate Torque
#         data[t, 1] = np.nan  # TODO math
#         # Make Array of Input voltage and corresponding torque
#     # Label Data based on if previous value was
#         if t > 0:
#             data[t, 2] = data[t - 1, 1]
#     # less than (0) or greater than (1) new value
#     # First value is always zero
    if type(trials) is list:
        brakeStrength = np.asarray(trials)
        trials = len(trials)
    elif isinstance(trials, np.ndarray):
        brakeStrength = trials
        trials = len(trials)
    else:
        brakeStrength = np.random.random_integers(0, 1000, (trials,)) / 10.0
    if atrials > 0:
        step = 40
        cutoff = 50
        asymSteps = np.zeros(atrials)
        for i in range(1, atrials // 2, 2):
            asymSteps[i] = min(1000 - cutoff, asymSteps[i - 1] + 2 *
                               np.random.random_integers(0, step))
            asymSteps[i + 1] = max(0, asymSteps[i] - 1 *
                                   np.random.random_integers(0, step))
        asymSteps[atrials // 2] = 1000
        for i in range(atrials // 2 + 1, atrials - 1, 2):
            asymSteps[i] = max(0 + cutoff, asymSteps[i - 1] - 2 *
                               np.random.random_integers(0, step))
            asymSteps[i + 1] = min(1000, asymSteps[i] + 1 *
                                   np.random.random_integers(0, step))
        asymSteps[-1] = max(0 + cutoff, asymSteps[-2] - 2 *
                            np.random.random_integers(0, step))
        brakeStrength = np.append(brakeStrength, asymSteps / 10)
        print(np.shape(brakeStrength))
        plt.plot(brakeStrength)
        plt.show()
    currentScale = 1000 / 100
    pause = 0
    motorSpeed = 5  # [20, 20, 20, 20, 20]
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
    intError = 0
    lastError = 0
    data = np.full([int(fullTime * pts), 5], np.nan)
    if pause <= 0:

        #warm-up
        # CMF.setMotorSpeed(rc, motorSpeed)
        # time.sleep(1)
        print('Starting warmup')
        start = time.time()
        looptime = start
        while looptime - start < 30:
            setSpeed = motorSpeed  # [int(np.floor(currTime / timeLength))]
            acSpeed = CMF.readAcSpeed(rc)
            error = setSpeed - acSpeed
            derror = error - lastError
            intError += error
            command = P * error + D * derror + I * intError
            CMF.setMotorSpeed(rc, command)
            lastError = error
            looptime = time.time()
    for point in range(0, len(brakeStrength)):

        # initialize Data

        # Main Loop
        if pause > 0:
            intError = 0
            lastError = 0
            CMF.setMotorSpeed(rc, motorSpeed)
            time.sleep(1)
        stepTime = 0.0
        currTime = stepTime + timeLength * point
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
            brakeTorque = int(round(
                currentScale * brakeStrength[int(np.floor(currTime / timeLength))]))
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
            currTime = stepTime + timeLength * point
        if pause > 0:
            CMF.stopMotor(rc)
            time.sleep(pause * brakeStrength[point] / 100.0)
    CMF.stopMotor(rc)
    np.savetxt(currdir + fname + '.csv', data, fmt='%.2f', delimiter=',', newline='\n',
               header=('Time, setPoint, Actual Brake Current, MotorCurrent, MotorSpeed, trials: %d , atrials: %d , pts: %d , timeLength: %0.2f' % (trials, atrials, pts, timeLength)), footer='', comments='# ')
    np.savetxt(currdir + 'BrakeCommands' + fname  + '.csv', brakeStrength, fmt='%.1f', delimiter=',', newline='\n',
               header='', footer='', comments='# ')
    brake.setTorque(Mc, 0)
    print('brake command sent')
    brake.close(Nb, Mc)
    print('brake closed')
    return (data, brakeStrength)

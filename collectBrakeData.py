import numpy as np
import brake
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw
from ard_T import Ard_T
import time
import matplotlib.pyplot as plt

mode_dict = {'warmup': -1, 'settime': 0, 'temp': 1}
warmup_time = 7.5


def collectBrakeData(trials, currdir, fname, timeLength=12, pts=50,
                     atrials=0, mode='warmup', testSet=10, breed='PG188Test'):

    # Set up Warmup/Cooldown Mode Type
    if mode in mode_dict:
        modeID = mode_dict[mode]
    else:
        modeID = mode_dict["warmup"]

    # Set up Command List
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
        plt.plot(brakeStrength)
        plt.show()

    #
    warmupStrength = np.zeros(len(brakeStrength))
    if breed == 'PG188Test':
        warmupStrength[(trials + atrials // 2):] = np.ones(atrials // 2)
    # elif breed == 'PG188PlacidStepwiseTest':
    #     runs = len(brakeStrength)/31
    #     for r in range(runs):
    #         warmupStrength[(31*r+16):(31*r+31)] = np.full(16, )
    elif breed == 'PendTest' and brakeStrength[0] > 50:
        warmupStrength = np.full(len(brakeStrength), 100)

    currentScale = 1000 / 100

    pause = 0
    motorSpeed = 45  # [20, 20, 20, 20, 20]
    fullTime = timeLength * len(brakeStrength)

    # initialize devices
    print('Initializing')
    tc = Ard_T('COM3', 1)
    rc = RoboClaw('COM11', 0x80)
    Nb, Mc = brake.initNebula()

    dt = 1.0 / pts
    P = 5  # 7
    D = 3
    I = .15
    # P = 0
    # D = 0
    # I = 0
    # Create List of Commands
    intError = 0
    lastError = 0
    data = np.full([int(fullTime * pts), 7], np.nan)
    if pause <= 0:
        pass

    record = False
    stretch = True
    # Main Loop
    CMF.setMotorSpeed(rc, CMF.compPWM(motorSpeed, 0))
    time.sleep(0.5)
    for point in range(0, len(brakeStrength)):
        commandSent = False

        if modeID == mode_dict['settime'] and point % testSet == 0:
            stretch = False
            record = False
            brake.setTorque(Mc, 0)
        elif modeID == mode_dict['temp'] and not tc.isSafeTemp():
            # print('cooldown')
            stretch = False
            record = False
            setSpeed = 20
            brake.setTorque(Mc, 0)
        # if pause > 0:
        #     intError = 0
        #     lastError = 0
        #     CMF.setMotorSpeed(rc, motorSpeed)
        #     time.sleep(1)
        stepTime = 0.0
        currTime = stepTime + timeLength * point
        start = time.time()
        # PID loop begins here
        setSpeed = motorSpeed
        try:
            while stepTime < timeLength:
                # setSpeed = motorSpeed  # [int(np.floor(currTime / timeLength))]
                acSpeed = CMF.readAcSpeed(rc)
                error = setSpeed - acSpeed
                derror = error - lastError
                intError += error
                if record:
                    tcmd = brakeStrength[point]
                else:
                    tcmd = 0
                command = CMF.compPWM(setSpeed, tcmd) + P * \
                    error + D * derror + I * intError
                CMF.setMotorSpeed(rc, command)
                lastError = error
                if not(record) and point == 0:
                    if (time.time() - start > warmup_time):# and tc.isStartTemp(tc):
                        record = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                    else:
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point

                elif not stretch:
                    # criteria to start recording for each mode
                    ''' TODO
                    1) Regive previous brake command
                    2) Measure this new torque to be given as previous torque
                    3) give proper torque command
                    OR
                    1) List previous brake command as zero
                    OR
                    for legacy support, add seventh column that changes from zero if cooldown occured
                    what should it be? These are the questions for a wiser man
                    Intermediate Mode, add data to seventh column of future time
                    '''
                    setSpeed = 20
                    if modeID == 0 and time.time() - start > 60:
                        # print('Warmup Done')
                        stretch = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                        stretch = True
                    elif modeID > 0 and tc.isStartTemp():
                        stretch = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                        stretch = True
                elif stretch and not record:  # warmup from cooldown, meaning motor has sufficiently waited, now need new prev torque data
                    setSpeed = motorSpeed
                    brakeTorque = int(
                        round(currentScale * warmupStrength[point]))
                    brake.setTorque(Mc, brakeTorque)
                    stretchTime = time.time()
                    if stretchTime - start < timeLength:
                        data[int((np.floor((currTime + stretchTime - start) / dt))),
                             6] = CMF.readInCurrent(rc)
                    else:
                        record = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()

                elif record:
                    setSpeed = motorSpeed
                    if not(commandSent):
                        brakeTorque = int(round(
                            currentScale * brakeStrength[int(np.floor(currTime / timeLength))]))
                        brake.setTorque(Mc, brakeTorque)
                        commandSent = True

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
                    data[int(np.floor(currTime / dt)),
                         3] = CMF.readInCurrent(rc)

                    # Motor Speed
                    data[int(np.floor(currTime / dt)), 4] = acSpeed
                    # data[int(np.floor(currTime / dt)), 3] = setSpeed
                    data[int(np.floor(currTime / dt)), 5] = tc.readTemp()
                loopTime = time.time() - stepTime - start
                if loopTime < dt:
                    time.sleep(dt - loopTime)
                if record:
                    stepTime = time.time() - start
                    currTime = stepTime + timeLength * point
            if pause > 0:
                CMF.stopMotor(rc)
                time.sleep(pause * brakeStrength[point] / 100.0)
        except:
            np.savetxt(currdir + fname + '.csv', data, fmt='%.2f', delimiter=',',
                       newline='\n',
                       header=('Time, setPoint, Actual Brake Current, MotorCurrent, MotorSpeed, Temperature, Warmup Current, trials: %d , atrials: %d , pts: %d , timeLength: %0.2f'
                               % (trials, atrials, pts, timeLength)), footer='', comments='# ')
            np.savetxt(currdir + 'BrakeCommands' + fname + '.csv', brakeStrength, fmt='%.1f',
                       delimiter=',', newline='\n', header='', footer='', comments='# ')
    # close everything and save
    # TODO save partial data set in case of crash with trys and accepts
    CMF.stopMotor(rc)
    np.savetxt(currdir + fname + '.csv', data, fmt='%.2f', delimiter=',',
               newline='\n',
               header=('Time, setPoint, Actual Brake Current, MotorCurrent, MotorSpeed, Temperature, Warmup Current, trials: %d , atrials: %d , pts: %d , timeLength: %0.2f'
                       % (trials, atrials, pts, timeLength)), footer='', comments='# ')
    np.savetxt(currdir + 'BrakeCommands' + fname + '.csv', brakeStrength, fmt='%.1f',
               delimiter=',', newline='\n', header='', footer='', comments='# ')
    brake.setTorque(Mc, 0)
    print('brake command sent')
    brake.close(Nb, Mc)
    print('brake closed')
    return (data, brakeStrength)

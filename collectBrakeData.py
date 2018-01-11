import numpy as np
import brake
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw
from ard_T import Ard_T
import time
import matplotlib.pyplot as plt

mode_dict = {'warmup': -1, 'settime': 0, 'temp': 1, 'settemp': 2}
warmup_time = 120


def collectBrakeData(trials, currdir, fname, timeLength=12, pts=50,
                     atrials=0, mode='warmup', testSet=10, breed='PG188Test', stepwise=False):

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
        step = 35 * (200 / atrials)
        cutoff = 50
        forw = 2
        back = .75
        asymSteps = np.zeros(atrials)
        for i in range(1, atrials // 2, 2):
            asymSteps[i] = min(1000 - cutoff, asymSteps[i - 1] + forw *
                               np.random.random_integers(0, step))
            asymSteps[i + 1] = max(0, asymSteps[i] - back *
                                   np.random.random_integers(0, step))
        asymSteps[atrials // 2] = 1000
        for i in range(atrials // 2 + 1, atrials - 1, 2):
            asymSteps[i] = max(0 + cutoff, asymSteps[i - 1] - forw *
                               np.random.random_integers(0, step))
            asymSteps[i + 1] = min(1000, asymSteps[i] + back *
                                   np.random.random_integers(0, step))
        asymSteps[-1] = max(0 + cutoff, asymSteps[-2] - forw *
                            np.random.random_integers(0, step))
        brakeStrength = np.append(brakeStrength, asymSteps / 10)
        plt.plot(brakeStrength)
        plt.show()

    warmupStrength = np.zeros(len(brakeStrength))
    if breed == 'PG188Test':
        warmupStrength[(trials + atrials // 2):] = np.full(atrials // 2, 100)
    elif breed == 'PG188PlacidStepwiseTest':
        runs = len(brakeStrength) // 31
        for r in range(runs):
            warmupStrength[(31 * r + 15):(31 * r + 31)] = np.full(16, 100)
    elif breed == 'PendTest' and brakeStrength[0] > 50:
        warmupStrength = np.full(len(brakeStrength), 100)

    if stepwise:
        stepStrength = [0, 6.8, 13.6, 20.4, 27.2, 34, 40.8, 47.6, 54.4, 62.1, 69.9, 77.7, 85.4, 92.2,
                        99.4, 100, 99.4, 92.2, 85.4, 77.7, 69.9, 62.1, 54.4, 47.6, 40.8, 34, 27.2, 20.4, 13.6, 6.8, 0]
        stepStrength.extend(brakeStrength)
        brakeStrength = stepStrength
    if stepwise:
        warmStepup = [0] * 15 + [100] * 16
        warmStepup.extend(warmupStrength)
        warmupStrength = warmStepup
    currentScale = 1000 / 100
    pause = 0
    motorSpeed = 45  # [20, 20, 20, 20, 20]
    coolSpeed = 5
    fullTime = timeLength * len(brakeStrength)
    pointOffset = 0
    if stepwise:
        pointOffset = 31

    dt = 1.0 / pts
    P = 5  # 7
    D = .75
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

    # initialize devices
    print('Initializing')
    tc = Ard_T('COM3', 1)
    rc = RoboClaw('COM11', 0x80)
    Nb, Mc = brake.initNebula()
    print('Waiting for Motor to Cool Off')
    while not(tc.isStartTemp()):
        time.sleep(5)
    print('Motor Temp in Safe Range')
    record = False  # recording data
    stretch = True  # cooled down, ramp back up to speed
    jog = True  # warmed back up
    stepwiseON = stepwise
    # Main Loop
    CMF.setMotorSpeed(rc, CMF.compPWM(motorSpeed, 0))
    time.sleep(0.5)
    # ############################MAIN LOOP START###############################
    try:
        for point in range(0, len(brakeStrength)):
            print(point + 1 - pointOffset)
            if point > 30:
                stepwiseON = False
            commandSent = False
            if not(stepwiseON):
                if point > 0 and (modeID == mode_dict['settime'] or modeID == mode_dict['settemp']) and (point - pointOffset) % testSet == 0:
                    jog = False
                    stretch = False
                    record = False
                    brake.setTorque(Mc, 0)
                elif modeID == mode_dict['temp'] and not tc.isSafeTemp():
                    print('cooldown')
                    jog = False
                    stretch = False
                    record = False
                    brake.setTorque(Mc, 0)
            elif stepwiseON and modeID != mode_dict['warmup'] and point == 16:
                print('Stepwise Reset')
                jog = False
                stretch = False
                record = False
                brake.setTorque(Mc, 0)

            stepTime = 0.0
            currTime = stepTime + timeLength * point
            start = time.time()
            # PID loop begins here
            setSpeed = motorSpeed

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
                    # and tc.isWarmTemp():
                    if (time.time() - start > warmup_time):
                        print('warmed')
                        record = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                    else:
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point

    ################################COOLDOWN HERE########################################
                elif not stretch:
                    decel = 0.05
                    if setSpeed > coolSpeed:
                        setSpeed -= decel
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
                    # setSpeed = coolSpeed
                    if modeID == 0 and time.time() - start > 60:
                        # print('Warmup Done')
                        stretch = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                    elif modeID > 0 and tc.isStartTemp():
                        stretch = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
    ########################################Stretch, ramp back up to speed####################################################
                elif not jog:
                    accel = 0.01
                    setSpeed += accel
                    if setSpeed >= motorSpeed:
                        setSpeed = motorSpeed
                        jog = True
    #########################JOG -RECORD MAKEUP PREVIOUS TORQUE##########################################################
                elif jog and not record:  # warmup from cooldown, meaning motor has sufficiently waited, now need new prev torque data
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
    #######################RECORDING DATA HERE#######################################################
                elif record:
                    setSpeed = motorSpeed
                    if not(commandSent):
                        brakeTorque = int(round(
                            currentScale * brakeStrength[int(np.floor(currTime / timeLength))]))
                        brake.setTorque(Mc, brakeTorque)
                        commandSent = True

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
# #########################END MAIN LOOP ####################################
    except:  # in case recording is interrupted
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

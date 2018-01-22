import numpy as np
from brake import Brake
from CalibrationMotorFunctions import CMF
# from ard_T import Ard_T
import time
import matplotlib.pyplot as plt


'''
Script for interfacing with machine to run the motor and issuing brake
commands

trials- Either a list of commands or an integer length to make a list
        of random commands
currdir-directory for where to save data
fname-name of test
timeLength- Length of each command in seconds
pts-number of points to sample per second
atrials-number of points to collect up and down curves
(each curve gets atrials/2 points)
mode-How motor overheating is handled (overwritten to warmup)
testSet- number of brake commands to collect before cooling down in set modes
(not used)
breed-type of test
stepwise-boolean to determine whether or not to conduct calibration test
 before each test
'''

# Controller Addresses
roboclaw_add = 'COM7'
# ard_add = 'COM3'

# parameters
mode_dict = {'warmup': -1, 'settime': 0, 'temp': 1, 'settemp': 2}
# warmup - no temp control
# settime - no temp control, cooldown cycle after every testSet points
# settemp - only check temperature every testSet number of points

# in seconds
warmup_time = 120  # always before first test for all modes
cooldown_time = 60


def collectBrakeData(trials, currdir, fname, timeLength=12, pts=50,
                     atrials=0, mode='warmup', testSet=10,
                     breed='PG188Test', stepwise=False):

    # Set up Warmup/Cooldown Mode Type
    if mode in mode_dict:
        modeID = mode_dict[mode]
    else:
        modeID = mode_dict["warmup"]

    # overwriting temperature control, comment out to reinstate
    modeID = mode_dict["warmup"]
    # Set up Command List
    # Convert from List or Array
    if type(trials) is list:
        brakeStrength = np.asarray(trials)
        trials = len(trials)
    elif isinstance(trials, np.ndarray):
        brakeStrength = trials
        trials = len(trials)

    else:  # generate randomly from inputs
        brakeStrength = np.random.random_integers(0, 1000, (trials,)) / 10.0

    # generates crawl-ups and downs to trace hysteresis curves
    if atrials > 0:
        # (1 unit = 0.1% brake command)
        step = 35 * (200 / atrials)
        cutoff = 50  # prevents curve switching
        forw = 2  # scaler for intended direction
        back = .75  # scaler for nonintended direction
        margin = 30  # acceptable distance from cutoff
        asymSteps = np.zeros(atrials)

        # since the path is random, the crawl-ups don't always make it
        # reasonably up the curve, this iterates until it does
        while(asymSteps[atrials // 2] - 1 < 1000 - cutoff - margin or
              asymSteps[-1] > cutoff + margin):
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

            # plt.plot(asymSteps)
            # plt.show()
        brakeStrength = np.append(brakeStrength, asymSteps / 10)
    # only useful for temperature control
    warmupStrength = np.zeros(len(brakeStrength))
    if breed == 'PG188Test':
        warmupStrength[(trials + atrials // 2):] = np.full(atrials // 2, 100)
    elif breed == 'PG188PlacidStepwiseTest':
        runs = len(brakeStrength) // 31
        for r in range(runs):
            warmupStrength[(31 * r + 15):(31 * r + 31)] = np.full(16, 100)
    elif breed == 'PendTest' and brakeStrength[0] > 50:
        warmupStrength = np.full(len(brakeStrength), 100)

    # extra commands to include stepwise calibration every test
    if stepwise:
        stepStrength = [0, 6.8, 13.6, 20.4, 27.2, 34, 40.8, 47.6, 54.4, 62.1,
                        69.9, 77.7, 85.4, 92.2, 99.4, 100, 99.4, 92.2, 85.4,
                        77.7, 69.9, 62.1, 54.4, 47.6, 40.8, 34, 27.2, 20.4,
                        13.6, 6.8, 0]
        stepStrength.extend(brakeStrength)
        brakeStrength = stepStrength
    if stepwise:
        warmStepup = [0] * 15 + [100] * 16
        warmStepup.extend(warmupStrength)
        warmupStrength = warmStepup

    motorSpeed = 45  # [20, 20, 20, 20, 20]
    coolSpeed = 5  # if temperature control is used
    fullTime = timeLength * len(brakeStrength)

    # for labeling points if stepwise test is used
    pointOffset = 0
    if stepwise:
        pointOffset = 31

    dt = 1.0 / pts  # estimated runtime of each loop

    # PID tuning parameteres
    P = 5
    D = .75
    I = .15

    # intialize error for PID loop
    intError = 0
    lastError = 0

    # create large array to record Data
    data = np.full([int(fullTime * pts), 7], np.nan)

    # ########## initialize devices#############################################
    print('Initializing')
    # tc = Ard_T(ard_add, 1)
    rc = CMF(roboclaw_add)
    Nb = Brake()  # always intialize last
   # ##########################################################################
    # # safety for temp control, even if warmup mode
    # # disabled since no longer connected
    # print('Waiting for Motor to Cool Off')
    # while not(tc.isStartTemp()):
    #     time.sleep(5)
    # print('Motor Temp in Safe Range')

    '''With Temp Control, loop had 3 settings, recording was recording the data
    stretching would be a cooldown, when set to True, it meant it was done
     cooling down
    Jog- cooled down, but needed to get back up to speed for jog to be true,
    Finally- record would be true once it had a new previous data point 
    this was collecting that data point'''
    record = False  # recording data if True
    stretch = True  # cooled down, ramp back up to speed
    jog = True  # warmed back up

    # whether or Not to include stepwise test
    stepwiseON = stepwise

    # Main Loop
    rc.setFFSpeed(motorSpeed, 0)  # start up motor
    time.sleep(0.5)
    # ############################MAIN LOOP START##############################
    try:
        for point in range(0, len(brakeStrength)):
            print('%d of %d' % (point + 1 - pointOffset,
                                len(brakeStrength) - pointOffset))
            if point > 30:
                stepwiseON = False
            commandSent = False

            # At start of each new point, check criteria based on mode
            # set record/other settings to False if not met, starting cooldown
            if not(stepwiseON):
                if point > 0 and (modeID == mode_dict['settime'] or modeID == mode_dict['settemp']) and (point - pointOffset) % testSet == 0:
                    jog = False
                    stretch = False
                    record = False
                    Nb.setTorque(0)
                # elif modeID == mode_dict['temp'] and not tc.isSafeTemp():
                #     print('cooldown')
                #     jog = False
                #     stretch = False
                #     record = False
                #     Nb.setTorque(0)

            # not used now, but stepwise calibration could not be interrupted
            # by temp controls other than the midway point
            elif stepwiseON and modeID != mode_dict['warmup'] and point == 16:
                print('Stepwise Reset')
                jog = False
                stretch = False
                record = False
                Nb.setTorque(0)

            # reset time for each part of the loop
            stepTime = 0.0  # time passed for each command
            currTime = stepTime + timeLength * point  # total runtime
            start = time.time()

            # PID loop begins here
            setSpeed = motorSpeed
            while stepTime < timeLength:
                acSpeed = rc.readAcSpeed()
                error = setSpeed - acSpeed
                derror = error - lastError
                intError += error
                if record:
                    tcmd = brakeStrength[point]
                else:
                    tcmd = 0
                # calculate PWM from feedward and PID feedback
                command = CMF.compPWM(setSpeed, tcmd) + P * \
                    error + D * derror + I * intError
                CMF.setMotorSpeed(rc, command)
                lastError = error

                # motor runs for warmup time before recording first point
                if not(record) and point == 0:
                    if (time.time() - start > warmup_time):
                        print('warmed')
                        record = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                    else:
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point

    # ###############################COOLDOWN HERE############################
                elif not stretch:
                    decel = 0.05  # velocity ramp down
                    if setSpeed > coolSpeed:
                        setSpeed -= decel

                    # criteria to start recording for each mode
                    # for set amount of time, regardless of temperature
                    if modeID == 0 and time.time() - start > cooldown_time:
                        stretch = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
                    # based on Temperature
                    # elif modeID > 0 and tc.isStartTemp():
                    #     stretch = True
                    #     stepTime = 0.0
                    #     currTime = stepTime + timeLength * point
                    #     start = time.time()
    # ##########Stretch, ramp back up to speed###############################
                elif not jog:
                    accel = 0.01
                    setSpeed += accel
                    if setSpeed >= motorSpeed:
                        setSpeed = motorSpeed
                        jog = True
    # ########################JOG -RECORD MAKEUP PREVIOUS TORQUE###############
                elif jog and not record:
                    setSpeed = motorSpeed
                    brakeTorque = warmupStrength[point]
                    Nb.setTorque(brakeTorque)
                    stretchTime = time.time()
                    if stretchTime - start < timeLength:
                        data[int((np.floor((currTime + stretchTime - start) / dt))),
                             6] = rc.readInCurrent()
                    else:
                        record = True
                        stepTime = 0.0
                        currTime = stepTime + timeLength * point
                        start = time.time()
    # ######################RECORDING DATA HERE###############################
                elif record:
                    setSpeed = motorSpeed
                    timeStamp = int(np.floor(currTime / dt))
                    # only send brake command once per loop
                    if not(commandSent):
                        brakeTorque = brakeStrength[point]
                        commandSent = Nb.setTorque(brakeTorque)

                    # TimeStamp
                    data[timeStamp, 0] = currTime

                    # Brake Command
                    data[timeStamp, 1] = brakeStrength[point]

                    # Actual Brake Reading
                    data[timeStamp, 2] = Nb.readCurrent()

                    # Motor Current
                    data[timeStamp, 3] = rc.readInCurrent()

                    # Motor Speed
                    data[timeStamp, 4] = acSpeed
                    # Temperature
                    # data[int(np.floor(currTime / dt)), 5] = tc.readTemp()

                # calculates actual loop time to determine if it should wait
                loopTime = time.time() - stepTime - start
                if loopTime < dt:
                    time.sleep(dt - loopTime)

                # updates timestamp for recording, cooldown periods were not
                # recorded
                if record:
                    stepTime = time.time() - start
                    currTime = stepTime + timeLength * point
# #########################END MAIN LOOP ####################################
    except:  # in case recording is interrupted
        print('Error Occurred: Saving Progress')
        np.savetxt(currdir + fname + '.csv', data, fmt='%.2f', delimiter=',',
                   newline='\n',
                   header=('Time, setPoint, Actual Brake Current, MotorCurrent, MotorSpeed, Temperature, Warmup Current, trials: %d , atrials: %d , pts: %d , timeLength: %0.2f'
                           % (trials, atrials, pts, timeLength)), footer='', comments='# ')
        np.savetxt(currdir + 'BrakeCommands' + fname + '.csv', brakeStrength, fmt='%.1f',
                   delimiter=',', newline='\n', header='', footer='', comments='# ')

    # close everything and save
    rc.stopMotor()
    # saving before turning off the brake in case of bugs
    # saves data
    np.savetxt(currdir + fname + '.csv', data, fmt='%.2f', delimiter=',',
               newline='\n',
               header=('Time, setPoint, Actual Brake Current, MotorCurrent, MotorSpeed, Temperature, Warmup Current, trials: %d , atrials: %d , pts: %d , timeLength: %0.2f'
                       % (trials, atrials, pts, timeLength)), footer='', comments='# ')
    # saves brake Inputs
    np.savetxt(currdir + 'BrakeCommands' + fname + '.csv', brakeStrength, fmt='%.1f',
               delimiter=',', newline='\n', header='', footer='', comments='# ')
    Nb.close()
    print('brake closed')
    return (data, brakeStrength)

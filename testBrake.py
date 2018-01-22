from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
import pickle
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RiseFallSVM as svm
from BrakeController import Controller
import yaml

'''
Main Script for calibrating brake
Runs random trials (and atrials) before using support vector machine
analysis to fit hysteresis curves
Note: SVM no longer used in brake control, so some methodology in collecting
fully random commands may be outdated, leaving alone for now

It will save the parameters in a .pickle file
Currently only the rise and fall parameters are used for the controller,
saved in a separate file
'''


# custom function used for fitting, not really needed since everything is one
# variable
# def gf(data, *args, **kwargs):
#     val = args[0]
#     # global xParamLength
#     xPL = kwargs.get('xPL', None)
#     # print(xPL)
#     for i in range(1, len(args)):
#         i // xPL
#         # coefficients of ascending degree
#         val += args[i] * data[int(i >= xPL),

#                               :]**(int(i >= xPL) + (i) % xPL)
#     return val


# metadata to save for tests
brakeID = 1742
breed = 'PG188Test'
testID = '2'
currdir = 'data/' + str(brakeID) + '/' + breed + \
    '/' + breed + str(testID) + '/'
test = breed + str(testID)
overwrite = False  # overwrite data already in file
convert = True  # convert current to torque

# test function parameters (trials = 100, atrials = 200)
trials = 75
atrials = 150

# parameters to tune
# for SVM
C = 1000
gamma = 1

# order of boundary equation in SVM
boundXL = 3

# order of polynomial fit for rising and falling curve
riseXL = 6
fallXL = 4

# makes filepath and runs test if it doesn't already exist
if not os.path.exists(currdir):
    os.makedirs(currdir)
if (overwrite or (not os.path.exists(currdir + test + '.csv'))):
    (data, brakeStrength) = collect(trials, currdir, test,
                                    atrials=atrials, timeLength=12,
                                    mode='warmup', breed=breed, stepwise=True)

# loads data from previous test
data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')


# plot figure 1 here(Raw Data)
time = data[:, 0]
ax = plt.subplot(411)
ax.plot(time,
        data[:, 1],)
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')

ax1 = plt.subplot(412)
ax1.plot(time,
         data[:, 3], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')

ax2 = plt.subplot(413)
ax2.plot(time,
         data[:, 4])
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')

ax2 = plt.subplot(414)
ax2.plot(time,
         data[:, 5])
plt.title('Motor Temp Vs. Time')
plt.ylabel('Temp (Celsius)')
plt.xlabel('Time(s)')

plt.savefig(currdir + test + 'figure1.png')
# plt.show()

# convert raw data to torques for analysis
compData = arrange(data, brakeStrength, currdir, test, convert=convert)

# extract atrials and trials from file header
with open(currdir + test + '.csv', newline='') as csvfile:
    header = next(csv.reader(csvfile, delimiter=',', quotechar='|'))
    header = ''.join(header)
    print(header)
    # import pts and timeLength here
    l = []
    for t in header.split():
        try:
            l.append(float(t))
        except ValueError:
            pass
    if len(l) > 1:
        trials = int(l[0])
        atrials = int(l[1])

# Plot Compressed Data
fig = plt.figure()
ax0 = fig.add_subplot(111, projection='3d')
ax0.scatter(compData[:, 0], compData[:, 1], compData[:, 2],
            c=compData[:, 0] - compData[:, 1], depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Prev Brake Command (%)')
ax0.set_zlabel('Torque (in-lb)')

# Plot Compdata with atrials labeled
ax0 = fig.add_subplot(111, projection='3d')
ax0.scatter(compData[:trials, 0], compData[:trials, 1], compData[:trials, 2],
            c='k', depthshade=False)
ax0.scatter(compData[trials:(trials + atrials // 2), 0],
            compData[trials:(trials + atrials // 2), 1],
            compData[trials:(trials + atrials // 2), 2],
            c='r', depthshade=False)
ax0.scatter(compData[(trials + atrials // 2):, 0],
            compData[(trials + atrials // 2):, 1],
            compData[(trials + atrials // 2):, 2],
            c='b', depthshade=False)
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Brake Command (%)')
ax0.set_ylabel(' Prev Brake Command (%)')
ax0.set_zlabel('Torque (in-lb)')
ncompData = compData[:, (0, 2)]
plt.savefig(currdir + test + 'figure2.png')
# plt.show()

# only do svm analysis if labeled data exists:
if atrials > 0:
    rData = ncompData[trials:(trials + atrials // 2), :]
    fData = ncompData[(trials + atrials // 2):, :]

    base = min(rData[:, -1])
    top = max(fData[:, -1])
    clf, scaler = svm.build(rData, fData, C=C, gamma=gamma)
    boundP = svm.simplify(clf, scaler, convert=convert, boundXL=boundXL)

    labels = svm.qlabel(boundP, ncompData)
    riseData, fallData = svm.split(compData, labels)

    # plot svm analysis of two curves and boundary
    fig2 = plt.figure()
    ax0 = fig2.add_subplot(111, )
    cmdRange = np.linspace(0.0, 100.0, 100)
    bpts = np.polyval(boundP, cmdRange)
    ax0.scatter(riseData[:, 0], riseData[:, -1],
                c='r')
    ax0.scatter(fallData[:, 0], fallData[:, -1],
                c='b', )  # depthshade=False)
    ax0.scatter(cmdRange, bpts, c='g')
    plt.title('Brake Commands Vs. Torque')
    ax0.set_xlabel('Brake Command (%)')
    ax0.set_ylabel(' Torque (%)')
    ax0.legend(('Lower Hysteresis Curve', 'Upper Hysteresis Curve',
                'Boundary'))
    plt.savefig(currdir + test + 'figure3.png')
    # plt.show()

    # Add intercepts here, useful for fitting
    base = min(riseData[:, -1])
    top = max(fallData[:, -1])
    base = 1.25
    top = 115

    # points to determine fit #This introduces fake derivative point but
    # points reaching the bottom should be the same anyway...
    rpoints = np.vstack(
        (riseData[:, (0, 1, 2)], np.tile([100, top, top], [1, 1])))
    fpoints = np.vstack(
        (fallData[:, (0, 1, 2)], np.tile([0, base, base], [1, 1])))

    # derivative
    rpoints[:, 1] = rpoints[:, 2] - rpoints[:, 1]
    fpoints[:, 1] = fpoints[:, 2] - fpoints[:, 1]

    # fits
    riseP = np.polyfit(rpoints[:, -1], rpoints[:, 0], riseXL)
    fallP = np.polyfit(fpoints[:, -1], fpoints[:, 0], fallXL)

    # load pLacid Data
    placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
    placidData[0, 0] = 1.25
    actTorque = placidData[:, 0]
    Command = placidData[:, 1]
    # make previous command column, was used in derivative analysis
    prevStrength = np.hstack(([0], placidData[:-1, 1]))
    placCMD = np.vstack((Command, prevStrength))

    # export data
    # NOTE: yaml order is coefficient power order, pickle is opposite, used by Numpy polval
    controlP = (clf, scaler, riseP, riseXL, fallP, fallXL)
    with open(currdir + 'Controller' + '.pickle', 'wb') as f:
        pickle.dump(controlP, f)
    with open(currdir + 'CurveP' + '.pickle', 'wb') as f:
        pickle.dump((riseP, fallP), f)
    with open(currdir + str(brakeID) + 'CurveP' + '.yaml', 'w') as f:
        yaml.dump(
            #{'lower_coefficents': [1,2,3], 'upper_coefficients': [1,2,3]}, f)
           {'lower_coefficents': riseP.tolist()[::-1], 'upper_coefficients': str(fallP.tolist()[::-1])}, f)

    # create model to test data
    cont = Controller(riseP, fallP)

    theoCMDS, labels = cont.model_DNA(actTorque)
    plt.figure()
    ax = plt.subplot(111)
    if convert:
        cmdRange = np.linspace(0, 115, 100)
        rpts = np.polyval(riseP, cmdRange)
        fpts = np.polyval(fallP, cmdRange)
        ax0 = ax.plot(Command, actTorque, 'k--',
                      theoCMDS[:16], actTorque[:16], 'b^',
                      theoCMDS[16:], actTorque[16:], 'g^',
                      rpts, cmdRange, 'r--',
                      fpts, cmdRange, 'b--')
        plt.legend(ax0, ('PlacidData', 'Lower Fit', 'Upper Fit',
                         'Lower Polynomial', 'Upper Polynomial'))
        plt.title('Brake Command Vs. Torque')
        plt.ylabel('Torque (in-lb)')
        plt.xlabel('Brake Command (%)')
        plt.savefig(currdir + test + 'figure4.png')

    else:
        cmdRange = np.linspace(0, 10, 100)
        rpts = np.polyval(riseP, cmdRange)
        fpts = np.polyval(fallP, cmdRange)
        ax0 = ax.plot(rpts, cmdRange, 'r--', fpts, cmdRange, 'b--')
        plt.legend(ax0, (
            'Lower Polynomial', 'Upper Polynomial'))
        plt.title('Brake Command Vs. Torque')
        plt.ylabel('Torque (in-lb)')
        plt.xlabel('Brake Command (%)')
        plt.savefig(currdir + test + 'figure4.png')
    # plt.show()

    # # This an early test against a specific dataset, deprecated
    # ranTestdir = 'data/PG188Test/PG188TestNewCoolCalTest3/'
    # ranTestname = 'PG188TestNewCoolCalTest3.csv'
    # if os.path.exists(ranTestdir):

    #     randata = np.loadtxt(ranTestdir + ranTestname,
    #                          delimiter=',', comments='# ')
    #     ranBrakeStrength = np.loadtxt(
    #         ranTestdir + 'BrakeCommands' + ranTestname,
    #         delimiter=',', comments='# ')
    #     rancompData = np.loadtxt(ranTestdir + 'CompUnconverted' + ranTestname,
    #                              delimiter=',', comments='#')

    #     cont.reset()
    #     # rancompData = compData
    #     randTorques = rancompData[:, -1]
    #     theoRandCMDs, labels = cont.model_dna(randTorques)

    #     fig2 = plt.figure()
    #     ax0 = fig2.add_subplot(111, projection='3d')
    #     # ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
    #     #             c='b', depthshade=False)
    #     ax0.scatter(rancompData[:, 2], rancompData[:, 1], theoRandCMDs - rancompData[:, 0],
    #                 c='r')
    #     plt.title('Brake Commands Vs. Torque')
    #     ax0.set_xlabel('Torque (in-lb)')
    #     ax0.set_ylabel(' Prev Torque (in-lb)')
    #     ax0.set_zlabel('Brake Command Error  (%)')
    #     # ax0.legend(('Actual CMD', 'Predicted CMD'))
    #     plt.savefig(currdir + test + 'figure5.png')
    #     plt.show()

    #     fig2 = plt.figure()
    #     ax0 = fig2.add_subplot(111)
    #     ax0.plot(theoRandCMDs - rancompData[:, 0])
    #     plt.title('Brake Command Error over Time')
    #     plt.ylabel('Absolute Error')
    #     plt.xlabel('Brake Command (%)')
    #     plt.savefig(currdir + test + 'figure6.png')
    #     # plt.show()
    #     theoRandCMDs = np.asarray(theoRandCMDs).T
    #     theoRandCMDs = theoRandCMDs.reshape(-1, 1)

    #     result = np.hstack((rancompData, theoRandCMDs))
    #     np.savetxt(currdir + 'Result' + test + '.csv', result, fmt='%.3f', delimiter=',', newline='\n',
    #                header='Actual Command, Previous Torque, Measured Torque, Predicted Command', footer='', comments='# ')

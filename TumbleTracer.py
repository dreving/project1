# TumbleTracer.py
# NoChaser.py

import pickle
import numpy as np

from scipy.optimize import fsolve
# import matplotlib
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from BrakeController import Controller


def find_slope(torque, dir):
    print(torque)
    if dir < 0:
        m = -0.0002 * torque**2 + 0.027 * torque + 0.1705

        # m = (10 / 12.5) * np.sqrt(torque / 38)
        # if torque > 90:
        #     m = (11 / 12.5) * np.sqrt(torque / 100)
    else:
        if torque < 20:
            m = 1.1
        elif torque < 30:
            m = 1.25
        elif torque < 45:
            m = 1.3
        elif torque < 65:
            m = 1.0
        elif torque < 80:
            m = 1.0
        elif torque < 90:
            m = 1.0
        else:
            m = 0.01
        m = -4E-05 * torque**2 - 0.0004 * torque + 1.2663
    return m


def point_slope_x(m, x1, y1, y):
    if m != 0:
        x = x1 + (y - y1) / m
    else:
        x = None
    return x


def point_slope_y(m, x1, y1, x):
    y = y1 + m * (x - x1)
    return y


def ladder_ends(riseP, fallP, direction, m, torque, command):
    """ return tuple of two torque values, between which the change
    in torque would be linear with current """
    if direction < 0:
        def f(y): return np.polyval(fallP, y) - \
            point_slope_x(m, command, torque, y)
        lowTorque = fsolve(f, torque)
        lowCMD = point_slope_x(m, command, torque, lowTorque)
        return ((lowCMD, lowTorque), (command, torque))
    else:
        def f(x): return np.polyval(riseP, x) - \
            point_slope_x(m, command, torque, x)
        highTorque = fsolve(f, torque)
        # point_slope_x(m, command, torque, highTorque)
        highCMD = np.polyval(riseP, highTorque)
        print(((command, torque), (highCMD, highTorque)))
        return ((command, torque), (highCMD, highTorque))


def ladder_pts(rungs, pts=50):
    m = (rungs[0][1] - rungs[1][1]) / (rungs[0][0] - rungs[1][0])
    YY = np.linspace(rungs[0][1], rungs[1][1], 50)
    XX = point_slope_x(m, rungs[0][0], rungs[0][1], YY)
    return XX, YY


def update_lines(num, torque, testData, testLine, testLineUp, cutoff,
                 conData, conLine):
    if num % 1 == 0:
        if num < cutoff:
            # pass
            testLine.set_data(testData[..., :num],
                              torque[..., :num])
        else:
            testLineUp.set_data(testData[..., cutoff:num],
                                torque[..., cutoff:num])
    # else:
    #     conLine.set_data(conData[..., :num//2],torque[...,:num//2])
    return testLine, conLine


breed = 'PG188Test'
testID = 'TumbleTest7Sarah'
cutoff = 100000000
currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
test = breed + str(testID)
# import data
rancompData = np.loadtxt(currdir + 'Comp' + test +
                         '.csv', delimiter=',', comments='# ')
cmds = rancompData[:, -1]

theoRandCMDs = np.zeros((len(cmds), 1))
labels = np.zeros((len(cmds), 1))

# import Controller
with open('data/' + 'ControllerI3' + '.pickle', 'rb') as g:
    (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
with open('data/' + 'boundPI3' + '.pickle', 'rb') as g:
    boundP = pickle.load(g)
cont = Controller(clf, scaler, p1, riseXL, p2, fallXL, boundP)

# main loop for each command
for i in range(len(cmds)):
    # if previous command doesn't match, reset, and give new bonus command
    if i > 0 and (cmds[i - 1] != rancompData[i, 1]):
        print('reset')
        cont.reset()
        cont.qmodel2([rancompData[i, 1]], [0])
    theoCMD, label = cont.qmodel2([cmds[i]], [rancompData[i, 0]])
    theoRandCMDs[i] = theoCMD
    labels[i] = label


# animate results over placid graph ##################################
# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=5, metadata=dict(artist='Me'), bitrate=3600)


fig1 = plt.figure()
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.13
plt.plot(placidData[:, 1], placidData[:, 0], 'k--')
riseP = p1[::-1]
fallP = p2[::-1]
testLine, = plt.plot([], [], 'b*')
testLineUp, = plt.plot([], [], 'r*')
conLine, = plt.plot([], [], 'g*')
thTor = np.linspace(0, 115)
thCMD = np.polyval(riseP, thTor)
plt.plot(thCMD, thTor, 'g--')
print(fallP)
print(ladder_ends(riseP,fallP,-1,1.07,59.99,55.32))
for pt in range(20, 100, 10):

    def torque2cmd(x):
        return np.polyval(riseP, x) - pt
    tor = fsolve(torque2cmd, 50)
    m = find_slope(tor, -1)
    print(m)
    tumXX, tumYY = ladder_pts(ladder_ends(riseP, fallP, -1, m, tor, pt))
    plt.plot(tumXX, tumYY, 'b')


for pt in range(20, 100, 10):

    def torque2cmd(x):
        return np.polyval(fallP, x) - pt
    tor = fsolve(torque2cmd, 50)
    m = find_slope(tor, 1)
    print(m)
    tumXX, tumYY = ladder_pts(ladder_ends(riseP, fallP, 1, m, tor, pt))
    plt.plot(tumXX, tumYY, 'r')
plt.xlim(5, 105)
plt.ylim(-5, 120)
plt.xlabel('Command(%)')
plt.ylabel('Torque (in-lb)')
plt.title(test)
plt.legend(('Placid Data', 'Actual Data', 'Simulation'))
line_ani = animation.FuncAnimation(fig1, update_lines, range(0, len(rancompData[:, -1])),
                                   fargs=(rancompData[:, -1],
                                          rancompData[:, 0], testLine,
                                          testLineUp, cutoff,
                                          theoRandCMDs[:, 0], conLine),
                                   interval=500, blit=False)
line_ani.save(currdir + test + 'Visualization.mp4', writer=writer)
plt.show()
# 3D error Plot of differences between commands###############################
# fig2 = plt.figure()
# ax0 = fig2.add_subplot(111, projection='3d')
# # ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
# #             c='b', depthshade=False)
# ax0.scatter(rancompData[:100, 2], rancompData[:100, 1],
#             theoRandCMDs[:100, 0] - rancompData[:100, 0],
#             c='g')
# ax0.scatter(rancompData[100:200, 2], rancompData[100:200, 1],
#             theoRandCMDs[100:200, 0] - rancompData[100:200, 0],
#             c='r')
# ax0.scatter(rancompData[200:, 2], rancompData[200:, 1],
#             theoRandCMDs[200:, 0] - rancompData[200:, 0],
#             c='b')
# plt.title('Brake Commands Vs. Torque')
# ax0.set_xlabel('Torque (in-lb)')
# ax0.set_ylabel(' Prev Torque (in-lb)')
# ax0.set_zlabel('Brake Command Error  (%)')
# # ax0.legend(('Actual CMD', 'Predicted CMD'))
# plt.show()

# fig2 = plt.figure()
# ax0 = fig2.add_subplot(111)
# ax0.plot(theoRandCMDs[:, 0] - rancompData[:, 0])
# plt.title('Brake Command Error over Time')
# plt.ylabel('Absolute Error')
# plt.xlabel('Datapoint')
# plt.show()

# result = np.hstack((rancompData, theoRandCMDs, labels))
# np.savetxt(currdir + 'Result' + test + '.csv', result, fmt='%.3f',
#            delimiter=',', newline='\n',
#            header='Actual Command, Previous Torque, Measured Torque, Predicted Command',
#            footer='', comments='# ')

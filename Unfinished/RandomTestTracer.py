# RandomTestTracer.py
# NoChaser.py

import pickle
import numpy as np
import matplotlib
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from BrakeController import Controller





def update_lines(num, torque, testData, testLine, conData, conLine):
    if num % 2 == 0: 
        testLine.set_data(testData[..., :num//2],torque[...,:num//2])
    # else:
    #     conLine.set_data(conData[..., :num//2],torque[...,:num//2])
    return testLine, conLine


breed = 'PG188Test'
testID = 'TumbleTest5Salvation'
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


#animate results over placid graph #################################################
# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=5, metadata=dict(artist='Me'), bitrate=3600)
m=10/12.5


fig1 = plt.figure()
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.13
plt.plot(placidData[:, 1], placidData[:, 0], 'k--')
testLine, = plt.plot([], [], 'r*')
conLine, = plt.plot([], [], 'g*')
plt.xlim(5, 105)
plt.ylim(-5, 120)
plt.xlabel('Command(%)')
plt.ylabel('Torque (in-lb)')
plt.title(test)
plt.legend(('Placid Data', 'Actual Data', 'Simulation'))
line_ani = animation.FuncAnimation(fig1, update_lines, len(theoRandCMDs)*2,
                                   fargs=(rancompData[:,-1],
                                       rancompData[:, 0], testLine,
                                       theoRandCMDs[:, 0], conLine),
                                   interval=1000, blit=False)
line_ani.save(currdir + test + 'Visualization.mp4', writer=writer)

# 3D error Plot of differences between commands#####################################
fig2 = plt.figure()
ax0 = fig2.add_subplot(111, projection='3d')
# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)
ax0.scatter(rancompData[:100, 2], rancompData[:100, 1], theoRandCMDs[:100, 0] - rancompData[:100, 0],
            c='g')
ax0.scatter(rancompData[100:200, 2], rancompData[100:200, 1], theoRandCMDs[100:200, 0] - rancompData[100:200, 0],
            c='r')
ax0.scatter(rancompData[200:, 2], rancompData[200:, 1], theoRandCMDs[200:, 0] - rancompData[200:, 0],
            c='b')
plt.title('Brake Commands Vs. Torque')
ax0.set_xlabel('Torque (in-lb)')
ax0.set_ylabel(' Prev Torque (in-lb)')
ax0.set_zlabel('Brake Command Error  (%)')
# ax0.legend(('Actual CMD', 'Predicted CMD'))
plt.show()

fig2 = plt.figure()
ax0 = fig2.add_subplot(111)
ax0.plot(theoRandCMDs[:, 0] - rancompData[:, 0])
plt.title('Brake Command Error over Time')
plt.ylabel('Absolute Error')
plt.xlabel('Datapoint')
plt.show()

result = np.hstack((rancompData, theoRandCMDs, labels))
np.savetxt(currdir + 'Result' + test + '.csv', result, fmt='%.3f', delimiter=',', newline='\n',
           header='Actual Command, Previous Torque, Measured Torque, Predicted Command', footer='', comments='# ')

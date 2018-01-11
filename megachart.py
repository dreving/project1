import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import os


# List of Torque Commands

breed = 'PendTest'

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList

# torqueList = pendTorqueList(115.0, 110.0, 0.0, -10, 1)


np.random.seed(44)
torqueList = np.random.random_integers(0, 1000, 20) / 10.0
trialTicks = []
for torque in torqueList:
    trialTicks.append(str(torque) + ' in-lb')
trialTicks = tuple(trialTicks)

# testIDs = [ 'Sawtooth1','45Sawtooth1Rising','44HigherDegreeSawtooth1Rising','44SawtoothRising5']
# testIDs = ['Sawtooth4', '45Sawtooth2Falling', '44HigherDegreeSawtooth2Falling','44SawtoothFalling5']
testIDs = ['RandomTorqueSeed44-LowerCurve', 'RandomTorqueSeed44-UpperCurve',
           'RandomTorqueSeed44-Avg of Curves', 'RandomTorqueSeed44-BoundaryMethod', 'RandomTorqueSeed44-NewMethod']
realTorques = np.zeros((len(testIDs), len(torqueList)))
error = np.zeros((len(testIDs), len(torqueList)))
fig = plt.figure(figsize=(2500 / 120, 2000 / 120))
ax0 = fig.add_subplot(111)


for testNum in range(len(testIDs)):
    testID = testIDs[testNum]
    test = breed + str(testID)
    currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
    compData = np.loadtxt(currdir + 'Comp' + test +
                          '.csv', delimiter=',', comments='# ')

    realTorques[testNum, :] = compData[:, -1]
    error[testNum, :] = realTorques[testNum, :] - torqueList

# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)
    ax0.scatter(range(len(trialTicks)), realTorques[testNum, :], marker="X")

ax0.scatter(range(len(trialTicks)), torqueList, marker="X")
plt.title('Actual Torque vs Command')
ax0.set_xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
ax0.set_ylabel('Torque (in-lb)')
leg = []
leg.extend(testIDs)
leg.append('Command')
ax0.legend(leg)
worstIndex = np.argmax(abs(error), axis=0)
print(worstIndex)
bestIndex = np.argmax(-abs(error), axis=0)
for t in range(len(torqueList)):
    print(t)
    # find best and worst
    # label Best
    worst = realTorques[worstIndex[t], t]
    best = realTorques[bestIndex[t], t]
    purp =realTorques[4, t] 

    plt.annotate(('%.1f' % (worst)) + ' in-lb', xy=(t, worst), xytext=(t + .1, worst), color = colors[worstIndex[t]],
                 arrowprops=dict(headlength=5, headwidth=5,
                                 facecolor=colors[worstIndex[t]], shrink=0.005),
                 )
    plt.annotate(('%.1f' % (best)) + ' in-lb', xy=(t, best), xytext=(t + .1, best), color = colors[bestIndex[t]], weight='bold',
                 arrowprops=dict(headlength=5, headwidth=5,
                                 facecolor=colors[bestIndex[t]], shrink=0.005),
                 )
    if bestIndex[t] != 4:
        plt.annotate(('%.1f' % (purp)) + ' in-lb', xy=(t, purp), xytext=(t + .1, purp), color = colors[4],
                     arrowprops=dict(headlength=5, headwidth=5,
                                     facecolor=colors[4], shrink=0.005),
                     )
plt.tight_layout()
plt.show()
fig=plt.figure(figsize=(2000 / 120, 800 / 120))

ax1=fig.add_subplot(211)
for testID in testIDs:
    test=breed + str(testID)
    currdir='data/' + breed + '/' + breed + str(testID) + '/'
    compData=np.loadtxt(currdir + 'Comp' + test +
                          '.csv', delimiter=',', comments='# ')

    realTorques=compData[:, -1]
    error=realTorques - torqueList
    ax1.scatter(range(len(trialTicks)), error, marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(in-lb)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
plt.legend(testIDs)
ax2=fig.add_subplot(212)
for testID in testIDs:
    test=breed + str(testID)
    currdir='data/' + breed + '/' + breed + str(testID) + '/'
    compData=np.loadtxt(currdir + 'Comp' + test +
                          '.csv', delimiter=',', comments='# ')

    realTorques=compData[:, -1]
    error=realTorques - torqueList
    ax2.scatter(range(len(trialTicks)), 100 *
                abs(error) / torqueList, marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(%)')
plt.xlabel('Datapoint')
plt.xticks(range(len(trialTicks)), trialTicks, rotation=17)
plt.tight_layout()
plt.legend(testIDs)
plt.show()

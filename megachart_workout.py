import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import copy
import os


# List of Torque Commands

breed = 'PendTest'
BBI_TList = [2.14, 4.28, 8.57, 10.71, 15.00, 17.14, 21.42, 25.71, 32.14, 38.56,
             42.85, 47.13, 53.56, 59.99, 64.27, 72.84, 79.27, 85.69, 92.12,
             96.41, 107.12]

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
          'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def pendTorqueList(pivot, start, end, inc, runs):
    torqueList = np.full(int((abs(end - start) // abs(inc)) * runs * 2), pivot)
    for i in range(0, len(torqueList) // 2):
        torqueList[2 * i + 1] = start + inc * (i // runs + 1)
    return torqueList


def exercise(peak, step):
    exer = []
    low = .55 * peak
    numsteps = np.ceil((peak - low) / step)
    exer.extend(np.linspace(peak, low, numsteps, endpoint=False))
    exer.extend(np.linspace(low, peak, numsteps))
    return exer


def workout(exerList, step, rest=False):
    cmds = []
    for i in range(len(exerList)):
        cmds.extend(exercise(exerList[i], step))
        if rest:
            cmds.append(0)
    return cmds

# torqueList = pendTorqueList(115.0, 110.0, 0.0, -10, 1)


np.random.seed(44)
# torqueList = np.random.random_integers(0, 1000, 20) / 10.0

TList_Shuff = copy.deepcopy(BBI_TList)
np.random.shuffle(TList_Shuff)
print(TList_Shuff)
# TList_Shuff = TList_Shuff[:5] #for shorter code tracing
# make workout from list
torqueList = workout(TList_Shuff, 3)
trialTicks = []
# for torque in torqueList:
#     trialTicks.append(str(torque) + ' in-lb')
tickInd = []
dataSpace = np.zeros(len(torqueList))
start = 0
spaceStart = 0
gr = 66/30.807
ts =20
pvi = []
for i in range(len(TList_Shuff)):
    torque = TList_Shuff[i]
    
    step = int(np.ceil(torque * (1 - .55) / 3))
    if i == 0:
        pvi.append(0)
    else:
        pvi.append(pvi[3*i - 1] + 1)
    pvi.append(pvi[3*i] + step)
    pvi.append(pvi[3*i+1] + step-1)
    dataSpace[spaceStart:spaceStart + 2 *
              step] = ts* np.linspace(start, start + 2, 2 * step)
    trialTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr,)))
    #trialTicks.append(('%.1f in-lb\n (%.1f lb)' % (.55*torque,.55*torque/gr)))
    trialTicks.append('')
    trialTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr)))
    start = start + 3
    spaceStart += 2 * step

tickInd = range(0, ts *len(trialTicks),ts)


testIDs = ['RandomTorqueSeed44-FinalTest_LOW',
           'RandomTorqueSeed44-FinalTest_TwoLane',
           'RandomTorqueSeed44-FinalTest_DNA']

realTorques = np.zeros((len(testIDs), len(torqueList)))
error = np.zeros((len(testIDs), len(torqueList)))
perError = np.zeros((len(testIDs), len(torqueList))) 
fig = plt.figure(figsize=(12000 / 120, 800 / 120))
ax0 = fig.add_subplot(111)


for testNum in range(len(testIDs)):
    testID = testIDs[testNum]
    test = breed + str(testID)
    currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
    compData = np.loadtxt(currdir + 'Comp' + test +
                          '.csv', delimiter=',', comments='# ')

    realTorques[testNum, :] = compData[:, -1]
    error[testNum, :] = realTorques[testNum, :] - torqueList
    perError[testNum,:] = 100*abs(error[testNum,:]) / torqueList
    ax0.scatter(dataSpace, realTorques[testNum, :], marker="X")

# errorTicks = copy.deepcopy(trialTicks)
errAvg = np.zeros((len(testIDs),len(TList_Shuff)))
perErrAvg = np.zeros((len(testIDs),len(TList_Shuff)))
realAvg = np.zeros((len(testIDs),len(TList_Shuff)))
for testNum in range(len(testIDs)):
    for i in range(len(TList_Shuff)):
        errAvg[testNum,i] = np.mean(error[testNum,pvi[3*i]:pvi[3*i + 2]+1])
        perErrAvg[testNum,i] = np.mean(perError[testNum,pvi[3*i]:pvi[3*i + 2]+1])
        realAvg[testNum,i] = np.mean(realTorques[testNum,pvi[3*i]:pvi[3*i + 2]+1])
print(pvi)
for i in range(len(TList_Shuff)):
    trialTicks[3*i] = trialTicks[3*i] + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f) ' % 
        (realTorques[0,pvi[3*i]],realTorques[0,pvi[3*i]]/gr,
            realTorques[2,pvi[3*i]],realTorques[2,pvi[3*i]]/gr,
            realTorques[1,pvi[3*i]],realTorques[1,pvi[3*i]]/gr))
    trialTicks[3*i+1] = 'Average Torque' + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f)' % 
        (realAvg[0,i],realAvg[0,i]/gr,
            realAvg[2,i],realAvg[2,i]/gr,
            realAvg[1,i],realAvg[1,i]/gr))
    trialTicks[3*i+2] = trialTicks[3*i+2] + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f)' % 
        (realTorques[0,pvi[3*i+2]],realTorques[0,pvi[3*i+2]]/gr,
            realTorques[2,pvi[3*i+2]],realTorques[2,pvi[3*i+2]]/gr,
            realTorques[1,pvi[3*i+2]],realTorques[1,pvi[3*i+2]]/gr))
# ax0.scatter(rancompData[:, 2], rancompData[:, 1], rancompData[:, 0],
#             c='b', depthshade=False)
    
trialTicks = tuple(trialTicks)
ax0.scatter(dataSpace, torqueList, marker="X")
plt.title('Actual Torque vs Command')
ax0.set_xlabel('Datapoint')
plt.xticks(tickInd, trialTicks, rotation=0)
ax0.set_ylabel('Torque (in-lb)')
leg = []
leg.extend(testIDs)
leg.append('Command')
ax0.legend(leg)
worstIndex = np.argmax(abs(error), axis=0)
bestIndex = np.argmax(-abs(error), axis=0)
# for t in range(len(torqueList)):
#     print(t)
#     # find best and worst
#     # label Best
#     worst = realTorques[worstIndex[t], t]
#     best = realTorques[bestIndex[t], t]
#     purp = realTorques[4, t]

#     plt.annotate(('%.1f' % (worst)) + ' in-lb', xy=(t, worst), xytext=(t + .1, worst), color=colors[worstIndex[t]],
#                  arrowprops=dict(headlength=5, headwidth=5,
#                                  facecolor=colors[worstIndex[t]], shrink=0.005),
#                  )
#     plt.annotate(('%.1f' % (best)) + ' in-lb', xy=(t, best), xytext=(t + .1, best), color=colors[bestIndex[t]], weight='bold',
#                  arrowprops=dict(headlength=5, headwidth=5,
#                                  facecolor=colors[bestIndex[t]], shrink=0.005),
#                  )
#     if bestIndex[t] != 4:
#         plt.annotate(('%.1f' % (purp)) + ' in-lb', xy=(t, purp), xytext=(t + .1, purp), color=colors[4],
#                      arrowprops=dict(headlength=5, headwidth=5,
#                                      facecolor=colors[4], shrink=0.005),
#                      )
plt.tight_layout()
ax0.margins(0.01)
plt.savefig('data/FinalResults.png')
plt.show()
errorTicks = []
for i in range(len(TList_Shuff)):
    torque = TList_Shuff[i]
    errorTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr,)))
    #trialTicks.append(('%.1f in-lb\n (%.1f lb)' % (.55*torque,.55*torque/gr)))
    errorTicks.append('')
    errorTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr,)))
    errorTicks[3*i] = errorTicks[3*i] + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f)' % 
        (error[0,pvi[3*i]],error[0,pvi[3*i]]/gr,
            error[2,pvi[3*i]],error[2,pvi[3*i]]/gr,
            error[1,pvi[3*i]],error[1,pvi[3*i]]/gr))
    errorTicks[3*i+1] = 'Average Error' + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f)' % 
        (errAvg[0,i],errAvg[0,i]/gr,
            errAvg[2,i],errAvg[2,i]/gr,
            errAvg[1,i],errAvg[1,i]/gr))
    errorTicks[3*i+2] = errorTicks[3*i+2] + ('\nLow: %.1f (%.1f)\nDNA: %.1f (%.1f)\n2Lane: %.1f (%.1f)' % 
        (error[0,pvi[3*i+2]],error[0,pvi[3*i+2]]/gr,
            error[2,pvi[3*i+2]],error[2,pvi[3*i+2]]/gr,
            error[1,pvi[3*i+2]],error[1,pvi[3*i+2]]/gr))

perTicks = []
for i in range(len(TList_Shuff)):
    torque = TList_Shuff[i]
    perTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr,)))
    #trialTicks.append(('%.1f in-lb\n (%.1f lb)' % (.55*torque,.55*torque/gr)))
    perTicks.append('')
    perTicks.append(('%.1f in-lb (%.1f lb)' % (torque,torque/gr,)))
    perTicks[3*i] = perTicks[3*i] + ('\nLow: %.1f%%\nDNA: %.1f%%\n2Lane: %.1f%%' % 
        (perError[0,pvi[3*i]],
            perError[2,pvi[3*i]],
            perError[1,pvi[3*i]],))
    perTicks[3*i+1] = 'Average % Error' + ('\nLow: %.1f%%\nDNA: %.1f%%\n2Lane: %.1f%%' % 
        (perErrAvg[0,i],
            perErrAvg[2,i],
            perErrAvg[1,i],))
    perTicks[3*i+2] = perTicks[3*i+2] + ('\nLow: %.1f%%\nDNA: %.1f%%\n2Lane: %.1f%%' % 
        (perError[0,pvi[3*i+2]],
            perError[2,pvi[3*i+2]],
            perError[1,pvi[3*i+2]],))

fig = plt.figure(figsize=(12000 / 120, 800 / 120))

ax1 = fig.add_subplot(211)
for testID in range(len(testIDs)):
    # test = breed + str(testID)
    # currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
    # compData = np.loadtxt(currdir + 'Comp' + test +
    #                       '.csv', delimiter=',', comments='# ')

    # realTorques = compData[:, -1]
    # error = realTorques - torqueList
    ax1.scatter(dataSpace, error[testID,:], marker="X")
plt.title('Error of Torque Command')
plt.ylabel('Error(in-lb)')
plt.xlabel('Datapoint')
plt.xticks(tickInd, errorTicks, rotation=0)
plt.legend(testIDs)
plt.plot(dataSpace,np.zeros(len(dataSpace)),'k--')
ax2 = fig.add_subplot(212)
# ax3 = fig.add_subplot(212)
for testID in range(len(testIDs)):
    # test = breed + str(testID)
    # currdir = 'data/' + breed + '/' + breed + str(testID) + '/'
    # compData = np.loadtxt(currdir + 'Comp' + test +
    #                       '.csv', delimiter=',', comments='# ')

    # realTorques = compData[:, -1]
    # error = realTorques - torqueList
    ax2.scatter(dataSpace, 100 *
                abs(error[testID,:]) / torqueList, marker="X")
    # ax3.scatter(dataSpace, 100 *
    #             abs(error) / torqueList, marker="X")
plt.title('Error of Torque Command')
ax2.set_ylim(0, 50.)  # outliers only
# ax3.set_ylim(200, 400)  # most of the data
plt.ylabel('Error(%)')
plt.xlabel('Datapoint')
plt.xticks(tickInd, perTicks, rotation=0)
plt.legend(testIDs)
plt.tight_layout()
plt.savefig('data/FinalErrorResults.png')
plt.show()

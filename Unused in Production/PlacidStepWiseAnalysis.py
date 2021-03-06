import numpy as np
import matplotlib.pyplot as plt
from naiveanalyze import naiveanalyze as analyze


def itoT(i):
    # T = -92.74 + 0.0111 * np.sqrt(35872000 * i + 34699500)
    # T = -93.1563 + 0.00965487 * np.sqrt(46320000 * i + 56800000) #for motor speed 10
    T = -120.941 + 0.0111358 * np.sqrt(40160000 * i + 90000000) #for motor speed 5
    T = -114.436 + 0.025641 * np.sqrt(7.8e6 * i + 1.52571e7) # motor speed five with pause
    T = -132.179 + 0.079*np.sqrt(895000* i + 2.19199e6) 
    return T


runs = 5
fname = 'data/PG188PlacidStepwiseTest13.csv'
data = np.loadtxt(fname, delimiter=',', comments='# ')
for i in range(np.shape(data)[0]):
    if data[i, 4] < 0 or data[i, 4] > 11:
        data[i, 4] = np.nan
brakeStrength = [0, 6.8, 13.6, 20.4, 27.2, 34, 40.8, 47.6, 54.4, 62.1, 69.9, 77.7, 85.4, 92.2,
                 99.4, 100, 99.4, 92.2, 85.4, 77.7, 69.9, 62.1, 54.4, 47.6, 40.8, 34, 27.2, 20.4, 13.6, 6.8, 0]
brakeStrength = brakeStrength * runs
brakeStrength = np.asarray(brakeStrength)
# print(np.shape(data))

# get average current values
cmds = len(brakeStrength)
timeLength = 3.0
pts = 150
avgCurrent = np.zeros((cmds, 1))
ax = plt.subplot(121)
# ax.plot(data[:,0],data[:,3],'k--')
for t in range(cmds):
    timeStart = int(timeLength * (t + .5) * pts)
    timeEnd = int(timeLength * (t + .90) * pts)
    avgCurrent[t] = np.nanmean(data[timeStart:timeEnd, 3])
    ax.plot(data[timeStart:timeEnd,0],data[timeStart:timeEnd,3])

# do Two Point current transformations
plt.show()
noLoadCurrent = avgCurrent[0]
peakCurrent = np.amax(avgCurrent)
motorTorquesTP = (115 - 2.5) / (peakCurrent - noLoadCurrent) * \
    (avgCurrent - noLoadCurrent) + 2.5

# load lake Placid data
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.13
placidData = np.tile(placidData, (runs, 1))
# Do least Squares fitting
# p = np.polyfit(avgCurrent[:15, 0] - noLoadCurrent, placidData[:15, 0], 1)
currTorData = np.vstack((placidData[:, 0], avgCurrent[:, 0])).T
p = analyze(currTorData, 2, True)
print(p)


# lsfit = np.polyval(p, avgCurrent)
# plot actual brake % data vs transformed torque
# plot lake Placid data

ax = plt.subplot(111)
# ax.plot(avgCurrent-1.25, placidData[:,0],np.linspace(0,18), 15*np.log(np.linspace(0,18)-1.25)+38)
ax.plot(avgCurrent, placidData[:, 0])
plt.title('Actual Current Vs. Placid Reported Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Current (Amps)')
plt.show()
ax = plt.subplot(121)
ax0 = ax.plot(placidData[:, 1], placidData[:, 0], 'k--', brakeStrength,
              motorTorquesTP, 'b^', brakeStrength, itoT(avgCurrent), 'r^')
plt.legend(ax0, ('PlacidData', 'Two Point', 'Square Root Fit'))
plt.title('Brake Command Vs. Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')
ax = plt.subplot(122)
print(np.shape(placidData[:, 0]))
print(np.shape(motorTorquesTP[:, 0]))
currError = (itoT(avgCurrent).T - placidData[:, 0])
ax1 = ax.plot(brakeStrength, motorTorquesTP[:, 0] -
              placidData[:, 0], 'b^', brakeStrength.T, currError.T, 'r^')
plt.legend(ax1, ('Two Point', 'Least Squares'))
plt.title('Brake Command Vs. Error')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')

plt.show()


import numpy as np
import matplotlib.pyplot as plt
from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
from scipy.optimize import curve_fit
import os
# set up equation to work with sci.curve fit
breed = 'PG188PlacidStepwiseTest'


def itoT(i, p0,p1,p2,p3):
    T = p0 + p1 * np.sqrt(p2 * i + p3)
    return T


runs = 5
testID = 15
test = breed + str(testID)
currdir = 'data/' + breed + '/' + breed + str(testID) + '/'

brakeStrength = [0, 6.8, 13.6, 20.4, 27.2, 34, 40.8, 47.6, 54.4, 62.1, 69.9, 77.7, 85.4, 92.2,
                 99.4, 100, 99.4, 92.2, 85.4, 77.7, 69.9, 62.1, 54.4, 47.6, 40.8, 34, 27.2, 20.4, 13.6, 6.8, 0]
brakeStrength = brakeStrength * runs
# brakeStrength = [0, 100, 0]
if not os.path.exists(currdir):
    os.makedirs(currdir)
if not os.path.exists(currdir + test + '.csv'):
    (data, brakeStrength) = collect(brakeStrength, currdir, test)
data = np.loadtxt(currdir + test + '.csv', delimiter=',', comments='# ')
brakeStrength = np.loadtxt(currdir + 'BrakeCommands' +
                           test + '.csv', delimiter=',', comments='# ')
# plot here
time = data[:, 0]
ax = plt.subplot(311)
ax.plot(time,
        data[:, 2])
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(312)
ax1.plot(time, data[:, -2], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(313)
ax2.plot(time, data[:, -1])
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')
plt.savefig(currdir + test + 'figure1.png')
# plt.show()

# analyze but don't convert
compData = arrange(data, brakeStrength, currdir, test, convert=False)
avgCurrent = compData[:, -1]

# load lake Placid data
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.13
placidData = np.tile(placidData, (runs, 1))
# Do least Squares fitting
# p = np.polyfit(avgCurrent[:15, 0] - noLoadCurrent, placidData[:15, 0], 1)
#currTorData = np.vstack((placidData[:, 0], avgCurrent)).T

# replace with square root fit
# p = analyze(currTorData, 2, True)
p, cov = curve_fit(itoT, avgCurrent, placidData[:, 0],[-121,0.0111,40160000,900000000] )
print(p)


# lsfit = np.polyval(p, avgCurrent)
# plot actual brake % data vs transformed torque
# plot lake Placid data

ax = plt.subplot(111)
print(np.shape(avgCurrent))
for r in range(runs):
    ax.plot(avgCurrent[r*31:(31*r+16)], placidData[31*r:31*r+16, 0],'b--')
    ax.plot(avgCurrent[r*31+16:(31*r+31)], placidData[31*r+16:31*r+31, 0],'r--')
plt.title('Actual Current Vs. Placid Reported Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Current (Amps)')
plt.savefig(currdir + test + 'figure2.png')
# plt.show()

ax = plt.subplot(121)
ax0 = ax.plot(placidData[:, 1], placidData[:, 0],
              'k--', brakeStrength, itoT(avgCurrent, *p), 'r^')
plt.legend(ax0, ('PlacidData', 'Square Root Fit'))
plt.title('Brake Command Vs. Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')
ax = plt.subplot(122)
currError = (itoT(avgCurrent, *p).T - placidData[:, 0])
ax1 = ax.plot(brakeStrength.T, currError.T, 'r^')
plt.legend(ax1, ('Square Root Fit'))
plt.title('Brake Command Vs. Error')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')
plt.savefig(currdir + test + 'figure3.png')
# plt.show()

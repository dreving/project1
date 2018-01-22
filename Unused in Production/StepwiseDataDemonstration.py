from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt
global T0


def itoT(i):
    p0 = -93.1
    p1 = 67.94
    p2 = 1.297
    p0 = -103.9897
    p1 = 70.001
    p2 = 1.5687
    T = p0 + p1 * np.sqrt(i + p2) - T0
    return T


T0 = 1.25

print(fsolve(itoT, .7))
T0 = 115
print(fsolve(itoT, 8.4))


# Import Placid DATA and test of desired Fit, 26
placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
placidData[0, 0] = 1.13
compData = np.loadtxt(
    'data/PG188PlacidStepwiseTest/PG188PlacidStepwiseTest26/CompUnconvertedPG188PlacidStepwiseTest26.csv', delimiter=',', comments='# ')
avgCurrent = compData[:, -1]

# Plug in +-0.1 amps for each point in Lake placid data
errBar = np.zeros((2, len(avgCurrent)))
for point in range(len(avgCurrent)):
    curr = avgCurrent[point]
    errBar[0, point] = abs(itoT(curr - .1) - itoT(curr))
    errBar[1, point] = abs(itoT(curr + .1) - itoT(curr))
print(errBar)

# Plot only upswing for on upswing to determine errorbars
# Plot Error bar graph with grid
ax = plt.subplot(111)
runs = 1
x = avgCurrent[:16]
T0 = 0
y = itoT(x)
for r in range(runs):
    ax.plot(avgCurrent[r * 31:(31 * r + 16)],
            placidData[31 * r:31 * r + 16, 0], 'b--')
    ax.plot(avgCurrent[r * 31 + 16:(31 * r + 31)],
            placidData[31 * r + 16:31 * r + 31, 0], 'r--')
    ax.errorbar(x, y, errBar[:,:16],ecolor='green',mfc='green',mec='green')
plt.title('Actual Current Vs. Placid Reported Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Current (Amps)')
plt.legend(('Actual Rising Data', ' Actual Falling Data', 'Fit w/Error Bars'))

plt.show()




# Reuse Error but plot on Lake Placid Graph
ax = plt.subplot(111)
ax0 = ax.errorbar(placidData[:, 1], placidData[:, 0],errBar)
plt.title('Brake Command Vs. Torque')
plt.ylabel('Torque (in-lb)')
plt.xlabel('Brake Command (%)')
plt.show()
from collectBrakeData import collectBrakeData as collect
from arrangeBrakeData import arrangeBrakeData as arrange
from mvnaiveanalyze import mvnaiveanalyze as analyze
import numpy as np
import matplotlib.pyplot as plt

test = 'PG188Test1.csv'
# (data, BrakeStrength) = collect(150, test)
data = np.loadtxt('data/'+test, delimiter=',', comments='# ')
for i in range(np.shape(data)[0]):
        if data[i,4] < 0 or data[i,4] > 11:
            data[i,4] = np.nan
BrakeStrength = np.loadtxt('data/BrakeCommands'+test, delimiter=',', comments='# ')

time = data[:,0]
# plot here
ax = plt.subplot(411)
ax.plot(time,
        data[:, 2],)
# plt.legend()
plt.title('Brake Command Vs. Time')
plt.ylabel('Current (%)')
plt.xlabel('Time(s)')
ax1 = plt.subplot(412)
ax1.plot(time,
         data[:, 4], label='Motor Current')
plt.legend()
plt.title('Motor Current Vs. Time')
plt.ylabel('Current (Amps)')
plt.xlabel('Time(s)')
ax2 = plt.subplot(413)
ax2.plot(time,
         data[:, 5])
# plt.legend()
plt.title('Speed Vs. Time')
plt.ylabel('Speed (%)')
plt.xlabel('Time(s)')

plt.show()
# compData = arrange(data, BrakeStrength, test)
# p = analyze(compData, 10, True)
# print(p)

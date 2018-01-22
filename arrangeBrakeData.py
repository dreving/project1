import numpy as np
from CalibrationMotorFunctions import CMF
import csv
from scipy.optimize import curve_fit

'''
Function for converting raw data into an average torque for each command
data- raw numpy array exported by collectBrakeData
BrakeStrength- List of Commands
currdir- string of file directory for saving tests and locating data
fname- name of file to save if not None
timeLength and pts- length of time for recording data and number of points
collected per second, extracted from data file to prevent error
convert-boolean for whether or not to convert average current to torque
'''


# used in curve fitting
def itoT(i, p0, p1, p2):
    T = p0 + p1 * np.sqrt(i + p2)
    return T


def arrangeBrakeData(data, BrakeStrength, currdir, fname=None, timeLength=3,
                     pts=150, convert=True):

    # Import timeLength and pts from data, else use default
    if fname is not None:
        with open(currdir + fname + '.csv', newline='') as csvfile:
            header = next(csv.reader(csvfile, delimiter=',', quotechar='|'))
            header = ''.join(header)

            # import pts and timeLength here
            l = []
            for t in header.split():
                try:
                    l.append(float(t))
                except ValueError:
                    pass
            if len(l) > 3:
                timeLength = l[3]
                pts = l[2]

    # filter obvious errors
    for i in range(np.shape(data)[0]):
        if data[i, 3] < 0 or data[i, 3] > 11:
            data[i, 3] = np.nan

    cmds = len(BrakeStrength)
    avgCurrent = np.zeros((cmds, 1))
    # extra column used for cooldowns
    stretchCol = np.zeros((cmds, 1))

    # analysis for compressing data into average readings ber trial
    for t in range(cmds):
        # only use latter part of data
        timeStart = int(timeLength * (t + .7) * pts)
        timeEnd = int(timeLength * (t + .9) * pts)
        # filter
        udata = data[timeStart:timeEnd, 3]
        umean = np.nanmean(udata)
        ustd = np.nanstd(udata)
        filteredData = udata[abs(udata - umean) < 2 * ustd]
        avgCurrent[t] = np.nanmean(filteredData)

        # check for cooldowns and puts in temporary column
        if np.shape(data)[1] > 6:
            udata = data[timeStart:timeEnd, 6]
            umean = np.nanmean(udata)
            ustd = np.nanstd(udata)
            filteredData = udata[abs(udata - umean) < 2 * ustd]
            stretchCol[t] = np.nanmean(filteredData)

    # do Two Point current transformations
    if convert:
        p0 = None
        p1 = None
        p2 = None
        placidData = np.genfromtxt('data/ActualPlacidData.csv', delimiter=',')
        placidData[0, 0] = 1.13

        # check if stepwise test was included in data set
        if all(BrakeStrength[v] == placidData[v, 1] for v in range(31)):
            stepwisecurr = avgCurrent[:31]
            np.reshape(stepwisecurr, (31,))
            p, cov = curve_fit(
                itoT, stepwisecurr[:, 0], placidData[:, 0],
                [-121, 0.0111 * np.sqrt(40160000), 900000000 / 40160000])
            p0 = p[0]
            p1 = p[1]
            p2 = p[2]
            BrakeStrength = BrakeStrength[31:]
            avgCurrent = avgCurrent[31:]
            cmds = len(BrakeStrength)

        # handles conversion
        avgTorque = CMF.itoT(avgCurrent, p0, p1, p2)
        avgTorque = avgTorque[:, 0]
        prevTorque = np.hstack(([1.25], avgTorque[:-1]))

        # check cooldown column
        for t in range(cmds):
            if stretchCol[t] > 0:
                prevTorque[t] = stretchCol[t]
        compData = np.vstack((BrakeStrength, prevTorque, avgTorque)).T

        if fname is not None:
            np.savetxt(currdir + 'Comp' + fname + '.csv', compData, fmt='%.3f', delimiter=',', newline='\n',
                       header='setPoint, prevTorque, Torque', footer='', comments='# ')

    else:  # save unconverted, but average current readings
        avgCurrent = avgCurrent[:, 0]
        prevCurrent = np.hstack(([0], avgCurrent[:-1]))
        compData = np.vstack((BrakeStrength, prevCurrent, avgCurrent)).T
        # load lake Placid data
        if fname is not None:
            np.savetxt(currdir + 'CompUnconverted' + fname + '.csv', compData, fmt='%.3f', delimiter=',', newline='\n',
                       header='setPoint, prevCurrent, Current', footer='', comments='# ')
    return compData

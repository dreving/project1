import numpy as np
import CalibrationMotorFunctions as CMF
import csv


def arrangeBrakeData(data, BrakeStrength, currdir, fname=None, timeLength=3,
                     pts=150, convert=True):
    # Import timeLength and pts from data, else use default
    if fname is not None:
        with open(currdir + fname + '.csv', newline='') as csvfile:
            header = next(csv.reader(csvfile, delimiter=',', quotechar='|'))
            header = ''.join(header)
            # print(header)
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

    for i in range(np.shape(data)[0]):
        if data[i, 3] < 0 or data[i, 3] > 11:
            data[i, 3] = np.nan
    cmds = len(BrakeStrength)
    avgCurrent = np.zeros((cmds, 1))
    stretchCol = np.zeros((cmds, 1))
    for t in range(cmds):
        # typically .25 and .75
        timeStart = int(timeLength * (t + .7) * pts)
        timeEnd = int(timeLength * (t + .9) * pts)
        # filter
        udata = data[timeStart:timeEnd, 3]
        umean = np.nanmean(udata)
        ustd = np.nanstd(udata)
        filteredData = udata[abs(udata - umean) < 2 * ustd]
        avgCurrent[t] = np.nanmean(filteredData)
        if np.shape(data)[1] > 6:
            udata = data[timeStart:timeEnd, 6]
            umean = np.nanmean(udata)
            ustd = np.nanstd(udata)
            filteredData = udata[abs(udata - umean) < 2 * ustd]
            stretchCol[t] = np.nanmean(filteredData)
    # do Two Point current transformations
    if convert:
        avgTorque = CMF.itoT(avgCurrent)
        # for i in range(len(avgTorque)):
        #     avgTorque[i] = max(1.25, avgTorque[i])
        avgTorque = avgTorque[:, 0]
        prevTorque = np.hstack(([1.25], avgTorque[:-1]))
        for t in range(cmds):
            if stretchCol[t] > 0:
                prevTorque[t] = stretchCol[t]
        compData = np.vstack((BrakeStrength, prevTorque, avgTorque)).T
        # load lake Placid data
        if fname is not None:
            np.savetxt(currdir + 'Comp' + fname + '.csv', compData, fmt='%.3f', delimiter=',', newline='\n',
                       header='setPoint, prevTorque, Torque', footer='', comments='# ')
    else:
        avgCurrent = avgCurrent[:, 0]
        prevCurrent = np.hstack(([0], avgCurrent[:-1]))
        compData = np.vstack((BrakeStrength, prevCurrent, avgCurrent)).T
        # load lake Placid data
        if fname is not None:
            np.savetxt(currdir + 'CompUnconverted' + fname + '.csv', compData, fmt='%.3f', delimiter=',', newline='\n',
                       header='setPoint, prevCurrent, Current', footer='', comments='# ')
    return compData

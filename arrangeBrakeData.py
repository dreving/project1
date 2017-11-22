import numpy as np
import CalibrationMotorFunctions as CMF
import csv


def arrangeBrakeData(data, BrakeStrength, currdir, fname=None, timeLength=3, pts=150, convert=True):
    # filter
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
        if data[i, -2] < 0 or data[i, -2] > 11:
            data[i, -2] = np.nan
    cmds = len(BrakeStrength)
    avgCurrent = np.zeros((cmds, 1))
    for t in range(cmds):
        timeStart = int(timeLength * (t + .25) * pts)
        timeEnd = int(timeLength * (t + .75) * pts)
        avgCurrent[t] = np.nanmean(data[timeStart:timeEnd, -2])

    # do Two Point current transformations
    if convert:
        avgTorque = CMF.itoT(avgCurrent)
        # for i in range(len(avgTorque)):
        #     avgTorque[i] = max(1.25, avgTorque[i])
        avgTorque = avgTorque[:, 0]
        prevTorque = np.hstack(([1.25], avgTorque[:-1]))
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

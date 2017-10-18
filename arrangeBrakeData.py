import numpy as np
import CalibrationMotorFunctions as CMF


def arrangeBrakeData(data, BrakeStrength, fname, timeLength=3, pts=150):
    # filter
    for i in range(np.shape(data)[0]):
        if data[i, 4] < 0 or data[i, 4] > 11:
            data[i, 4] = np.nan
    cmds = len(BrakeStrength)
    avgCurrent = np.zeros((cmds, 1))
    for t in range(cmds):
        timeStart = int(timeLength * (t + .25) * pts)
        timeEnd = int(timeLength * (t + .75) * pts)
        avgCurrent[t] = np.nanmean(data[timeStart:timeEnd, 4])

    # do Two Point current transformations
    avgTorque = CMF.itoT(avgCurrent)
    # for i in range(len(avgTorque)):
    #     avgTorque[i] = max(1.25, avgTorque[i])
    prevStrength = np.hstack(([0], BrakeStrength[:-1]))
    avgTorque = avgTorque[:, 0]
    prevTorque = np.hstack(([1.25], avgTorque[:-1]))
    # print(np.shape(BrakeStrength))
    # print(np.shape(prevStrength))
    # print(np.shape(avgTorque[:,0]))
    # compData = np.vstack((BrakeStrength, prevStrength, avgTorque)).T
    compData = np.vstack((BrakeStrength, prevTorque, avgTorque)).T
    # load lake Placid data

    np.savetxt('data/Comp' + fname, compData, fmt='%.3f', delimiter=',', newline='\n',
               header='setPoint, prevsetPoint, Current', footer='', comments='# ')

    return compData

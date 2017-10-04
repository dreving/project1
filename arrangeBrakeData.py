import numpy as np
import CalibrationMotorFunctions as CMF


def arrangeBrakeData(data, BrakeStrength, fname, timeLength=3, pts=50):
    #filter
    for i in range(shape(data)[0]):
        if data[i,4] < 0 or data[i,4] > 11:
            data[i,4] = np.nan
    cmds = len(BrakeStrength)
    avgCurrent = np.zeros((cmds, 1))
    for t in range(cmds):
        timeStart = int(timeLength * (t + .25) * pts)
        timeEnd = int(timeLength * (t + .75) * pts)
        avgCurrent[t] = np.nanmean(data[timeStart:timeEnd, 4])

    # do Two Point current transformations
    avgTorque = CMF.itoT(avgCurrent)
    prevStrength = np.hstack([0], BrakeStrength[:-1])
    compData = np.vstack(BrakeStrength, prevStrength, avgTorque).T
    # load lake Placid data

    np.savetxt('Comp' + fname, compData, fmt='%.2f', delimiter=',', newline='\n',
               header='setPoint, prevsetPoint, Current', footer='', comments='# ')

    return compData

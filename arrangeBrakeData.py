import numpy as np
import CalibrationMotorFunctions as CMF


def arrangeBrakeData(data, BrakeStrength, fname, timeLength=3, pts=50):
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

import numpy as np
from scipy.optimize import curve_fit


class xyFit(object):
    def __init__(self, xLen, yLen):
        self.xLen = xLen
        self.yLen = yLen

    def fit(self, xydata, zdata ):
        p0 = .1 * np.ones(self.xLen + self.yLen)
        xydata=  xydata.T
        zdata = zdata.T
        # print(np.shape(xydata))
        # print(np.shape(zdata))
        # each column is a sample
        p, cov = curve_fit(self.xyeval, xydata, zdata, p0)
        return p

    def xyeval(self,data, *args, **kwargs):
        val = args[0]
        # global xParamLength
        xPL = self.xLen
        # print(xPL)
        for i in range(1, len(args)):
            i // xPL
            # coefficients of ascending degree
            val += args[i] * data[int(i >= xPL),

                                  :]**(int(i >= xPL) + (i) % xPL)
        return val

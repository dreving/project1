import numpy as np
from scipy.optimize import curve_fit


class rfit(object):
    def __init__(self, k, xParamLength, splitData, fold):
        self.k = k
        self.xParamLength = xParamLength
        self.splitdata = splitData
        self.fold = fold
        self.F = None  # set
        self.bestTest = None  # set
        self.bestRes = None  # set
        self.sseMax = 0.0  # set
        self.r2 = None  # set
        self.adr2 = None  # set
        self.sseMin = np.Inf  # set
        self.pbest = None  # set
        self.N = None  # set
        self.fill()

    def gf(self, data, *args, **kwargs):
        val = args[0]
        # global xParamLength
        xPL = kwargs.get('xPL', None)
        # print(xPL)
        if xPL is None:
            xPL = self.xParamLength
        for i in range(1, len(args)):
            i // xPL
            # coefficients of ascending degree
            val += args[i] * data[int(i >= xPL),

                                  :]**(int(i >= xPL) + (i) % xPL)
        return val

    def getF(self, prevSSE):
        self.F = (prevSSE - self.sseMax) / \
            (self.sseMax / (self.N - self.k))
        return self.F

    def fill(self):
        # TODO, fix train and test data
        for f in range(self.fold):
            testdata = self.splitdata[f]
            traindata = np.concatenate(
                self.splitdata[np.arange(len(self.splitdata)) != f], axis=1)
            p0 = np.ones(self.k)
            p, cov = curve_fit(self.gf, testdata[0:-1, :], testdata[-1, :], p0)
            # equation from polynomial form. I guess I'll need this anyway.
            # residuals = p[1]
            M = np.shape(traindata)[1]
            residuals = 0
            for i in range(0, M):
                # res = (np.polyval(p[0], testdata[i, 0]) - testdata[i, 1])
                res = self.gf(np.reshape(traindata[0:-1, i], (2, 1)), *p)
                residuals += (res)**2
                # print(residuals)
            self.N = np.shape(testdata)[1]
            error = 0
            # pbest = np.poly1d(0)
            resVals = []
            for i in range(0, self.N):
                # res = (np.polyval(p[0], testdata[i, 0]) - testdata[i, 1])
                res = self.gf(np.reshape(
                    testdata[0:-1, i], (2, 1)), *p) - testdata[-1, i]
                resVals.append(res)
                error += (res)**2
                # normalize do I divide by the original value here? Nah...
            # print(foldOverfit)
            z = testdata[-1, :]
            zbar = np.sum(testdata[-1, :]) / self.N
            ssres = error
            # ssreg = np.sum((yhat-ybar)**2)
            sstot = np.sum((z - zbar)**2)
            sse = ssres
            if sse > self.sseMax:
                self.sseMax = sse
            if sse < self.sseMin:  # most generalizeable
                self.sseMin = sse
                self.bestRes = resVals
                self.bestTest = testdata
                # yhat = np.polyval(p[0], testdata[i, 0])
                self.r2 = 1 - ssres / sstot
                self.adr2 = 1 - ((1 - self.r2) *
                                 (self.N - 1) / self.N - self.k - 1)
                self.pbest = (p, self.k, self.xParamLength)
            return self.pbest
# Use this class to keep data organized
# So now I will compare F values of past two
# best will be next one
# Increment based on that class's x's and y's
# put xparamlength as class variable and fit as class method

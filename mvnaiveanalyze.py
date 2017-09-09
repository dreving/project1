
def mvnaiveanalyze(data, fold=10, debug=False):
    """ Data = k+1xt Matrix k = number of independent variables
           t = number of data points
           last row is dependent variable """
    # Now have multiple variables, and stopping criteria for each one
    # use scipy.optimize.curve_fit
    # now build a function with different predictors
    # use t-tests to determine stopping criteria
    # 5*30 - at least 150 tests recommended
    # assume polynomial fit, for now, but not order of equation
    # increment power until overfit (test error > by training error
    # by significant amount)
    # scipy.optimize.curve_fit(f,xdata,ydata) <-allows initial guess
    # ydata = f(xdata, *params) + eps <- assumption
    # or numpy.polyfit(x,y,deg) <-easiest for now
    # TEST- Make function- generate random data, define bounds by what give original eq
    # overfit error = testerror - trainerror -compare slopes

    # split data set into training and test
    # np.random.shuffle shuffles columns
    stop = 0  # need to be true for both variables
    k = 2
    global xParamLength
    xParamLength = 2
    parray = []
    testArray = []
    resArray = []
    r2Array = []
    pressArray = []
    prevOverfit = np.Inf
    while not(stop > 1):
        data = data.T
        np.random.shuffle(data)
        data = data.T
        splitdata = np.array(np.array_split(data, fold, axis=1))
        sseMax = 0.0
        sseMin = np.inf
        for f in range(fold):

            # testdata = data[:len(data)/fold,:]
            # traindata = data[len(data)/fold:,:]
            # cross validate by shuffling
            # TODO change residual definitions

            testdata = splitdata[f]
            traindata = np.concatenate(
                splitdata[np.arange(len(splitdata)) != f], axis=1)
            # p = np.polyfit(traindata[:, 0], traindata[:, 1], k, None, True)
            p0 = np.ones(k)
            p, cov = curve_fit(gf, testdata[0:-1, :], testdata[-1, :], p0)
            # equation from polynomial form. I guess I'll need this anyway.
            # residuals = p[1]
            M = np.shape(traindata)[1]
            residuals = 0
            for i in range(0, M):
                # res = (np.polyval(p[0], testdata[i, 0]) - testdata[i, 1])
                res = gf(np.reshape(traindata[0:-1, i], (2, 1)), *p)
                residuals += (res)**2
            # print(residuals)

            N = np.shape(testdata)[1]
            error = 0
            # pbest = np.poly1d(0)
            resVals = []
            for i in range(0, N):
                # res = (np.polyval(p[0], testdata[i, 0]) - testdata[i, 1])
                res = gf(np.reshape(
                    testdata[0:-1, i], (2, 1)), *p) - testdata[-1, i]
                resVals.append(res)
                error += (res)**2
                # normalize do I divide by the original value here? Nah...
            # print(foldOverfit)

            z = testdata[-1, :]
            zbar = np.sum(testdata[-1, :]) / N
            ssres = error
            # ssreg = np.sum((yhat-ybar)**2)
            sstot = np.sum((z - zbar)**2)
            sse = ssres
            if sse > sseMax:
                sseMax = sse
            if sse < sseMin:  # most generalizeable
                sseMin = sse
                bestRes = resVals
                bestTest = testdata
                # yhat = np.polyval(p[0], testdata[i, 0])
                r2 = 1 - ssres / sstot
                adr2 = 1 - ((1 - r2) * (N - 1) / (N - k - 1))
                pbest = p

                # save data for r**2 value
        parray.append((pbest, k, xParamLength))
        testArray.append(bestTest)
        resArray.append(bestRes)
        pressArray.append(sseMax)
        r2Array.append((r2, adr2))

        # this constant is arbitrary TODO set to be standard error
        # if (prevOverfit != np.Inf) and (foldOverMax - prevOverfit) > prevOverfit:
        F = (prevOverfit - sseMax) / (sseMax/(N-k))
        crit = scipy.stats.f.ppf(q=cert, dfn=1, dfd=(N-k))
        # prob = scipy.stats.f.cdf(crit, dfn=3, dfd=39)
        if sseMax > prevOverfit:
            stop += 1
        else:
            stop = 0
        k += 1
        if (k % 2) == 0:
            xParamLength += 1
        prevOverfit = sseMax

    if debug:  # TODO convert to 3d plots
        # pass#plot stuff here, and run loop a few more times to be sure
        pts = 100
        xMin = min(data[0, :])
        xMax = max(data[0, :])
        yMin = min(data[1, :])
        yMax = max(data[1, :])
        xSpan = np.linspace(xMin, xMax, pts)
        ySpan = np.linspace(yMin, yMax, pts)
        xx, yy = np.meshgrid(xSpan, ySpan)
        coorGrid = np.asarray([np.reshape(xx, -1), np.reshape(yy, -1)])
        # print(np.shape(coorGrid))
        fig = plt.figure()
        if len(testArray) > 2:
            ax0 = fig.add_subplot(231, projection='3d')
            ax0.scatter(testArray[-3][0, :], testArray[-3]
                        [1, :], testArray[-3][2, :], c='k')
            ax0.plot_wireframe(coorGrid[0, :], coorGrid[1, :], gf(
                coorGrid, *(parray[-3][0]), xPL=parray[-3][2]), alpha=0.4)
            # ax0.title('r**2 = %.2f' % (r2Array[-3][0]))
            ax4 = fig.add_subplot(234, projection='3d')
            ax4.scatter(testArray[-3][0, :], testArray[-3]
                        [1, :], resArray[-3], c='r')

        ax1 = fig.add_subplot(232, projection='3d')
        ax1.scatter(testArray[-2][0, :], testArray[-2]
                    [1, :], testArray[-2][2, :], c='k')
        ax1.plot_wireframe(coorGrid[0, :], coorGrid[1, :], gf(
            coorGrid, *(parray[-2][0]), xPL=parray[-2][2]), alpha=0.4)
        ax5 = fig.add_subplot(235, projection='3d')
        ax5.scatter(testArray[-2][0, :], testArray[-2]
                    [1, :], resArray[-2], c='r')

        ax2 = fig.add_subplot(233, projection='3d')
        ax2.scatter(testArray[-1][0, :], testArray[-1]
                    [1, :], testArray[-1][2, :], c='k')
        ax2.plot_wireframe(coorGrid[0, :], coorGrid[1, :], gf(
            coorGrid, *(parray[-1][0]), xPL=parray[-1][2]), alpha=0.4)
        # plt.figure(1)

        ax6 = fig.add_subplot(236, projection='3d')
        ax6.scatter(testArray[-1][0, :], testArray[-1]
                    [1, :], resArray[-1], c='r')

        # plt.subplot(234)
        # plt.plot(testArray[-3][:, 0], resArray[-3], 'rx')
        # plt.title('r**2 = %.2f' % (r2Array[-3]))
        # plt.ylabel('Y')
        # plt.xlabel('X')

        # plt.subplot(235)
        # plt.plot(testArray[-2][:, 0], resArray[-2], 'rx')
        # plt.title('r**2 = %.2f' % (r2Array[-2]))
        # plt.ylabel('Y')
        # plt.xlabel('X')

        # plt.subplot(236)
        # plt.plot(testArray[-1][:, 0], resArray[-1], 'rx')
        # plt.title('r**2 = %.2f' % (r2Array[-1]))
        # plt.ylabel('Y')
        # plt.xlabel('X')
        plt.subplots_adjust(top=0.90, bottom=0.1, left=0.15, right=0.90,
                            hspace=0.49, wspace=0.7)

        plt.figure(2)
        nr2 = []
        ar2 = []
        for r in range(len(r2Array)):
            nr2.append(r2Array[r][0])
            ar2.append(r2Array[r][1])
        ax = plt.subplot(111)
        ax.plot(pressArray, 'r')
        # ax.plot(ar2, 'b')

    return parray[-3]
    # return polynomial, error in some form, r^2


def parseData(data):
    # rise = 0
    # fall = 1
    numPoints = len(data[:, 0])
    numRisePoints = np.sum(data[:, 2])
    riseData = np.zeros(numRisePoints, 2)
    fallData = np.zeros(numPoints, numRisePoints, 2)
    r = 0
    f = 0
    for i in range(numPoints):
        if data[i, 2]:
            fallData[f, :] = data[i, 0:2]
            f += 1
        else:
            riseData[r, :] = data[i, 0:2]
            r += 1

    return ([riseData, fallData])


# def simpleAnalysis(data, p0):
#     f = lambda x
#     return(scipy.optimize.curve_fit(lambda , data[:,0], data[:,1], p0)


# # naive analyze test
# import numpy as np
# import matplotlib.pyplot as plt
# ptest = np.array([.8, -.30, .40, -.8, 0, -.5])
# pts = 300
# under = 0
# over = 0
# for q in range(1000):
#     noise = np.random.normal(0, 5, pts)
#     x = [np.linspace(0.0, 15.0, pts)]
#     y = np.polyval(ptest, x) + noise
#     data = np.concatenate((x, y), axis=0).T
#     p = naiveanalyze(data, 10, True)
#     if len(p) < len(ptest):
#         under += 0.001
#     if len(p) > len(ptest):
#         over += 0.001
#     plt.show()
# print((under, over))


def gf(data, *args, **kwargs):
    val = args[0]
    # global xParamLength
    xPL = kwargs.get('xPL', None)
    # print(xPL)
    if xPL is None:
        xPL = xParamLength
    for i in range(1, len(args)):
        i // xPL
        # coefficients of ascending degree
        val += args[i] * data[int(i >= xPL),
                              :]**(int(i >= xPL) + (i) % xPL)
    return val


import numpy as np
import scipy
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.stats 
pts = 100
global xParamLength
xParamLength = 5
xdata = np.repeat(np.linspace(0.0, 1.0, pts), 3)
ydata = np.linspace(0.0, 3.0, 3 * pts)

zdata = gf(np.stack([xdata, ydata]), 1, 2, 3, 4, 5, 6, 7) + \
    np.random.normal(0, 1, 3 * pts)
data = np.stack([xdata, ydata, zdata])
popt = mvnaiveanalyze(data, 10, True)
print(popt)

plt.show()

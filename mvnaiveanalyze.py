import numpy as np
import scipy
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.stats


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
    xParamLength = 2
    #first set should be x^2 + c and x+y+c
    fitList = []
    while not(stop > 0):
        data = data.T
        np.random.shuffle(data)
        data = data.T
        splitData = np.array(np.array_split(data, fold, axis=1))
        xinc = rfit(k+1,xParamLength+1, splitData,fold)
        yinc = rfit(k+1,xParamLength,splitData,fold)
        if xinc.getF() > yinc.getF():
            F = xinc.F
            fitList.append(yinc)
            fitList.append(xinc)
        else:
            F = yinc.F
            fitList.append(xinc)
            fitList.append(yinc)
        # this constant is arbitrary TODO set to be standard error
        # if (prevOverfit != np.Inf) and (foldOverMax - prevOverfit) > prevOverfit:
        cert = .95  # confidence
        # this function produces the critical value based on the confidence
        crit = scipy.stats.f.ppf(q=cert, dfn=1, dfd=(xinc.N - xinc.k)) #check which N/k I use
        # Do I compare F to crit? Why did I stop here?
        # prob = scipy.stats.f.cdf(crit, dfn=3, dfd=39) # This function will be the inverse of ppf if needed
        # if sseMax > prevOverfit:

        #Stop Criteria Adjusted Here
        if F > crit:
            stop += 1
        else:
            stop = 0

        #X and y's updated here
        k = fitList[-1].k
        xParamLength = fitList[-1].xParamLength

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




# pts = 100
# global xParamLength
# xParamLength = 5
# xdata = np.repeat(np.linspace(0.0, 1.0, pts), 3)
# ydata = np.linspace(0.0, 3.0, 3 * pts)

# zdata = gf(np.stack([xdata, ydata]), 1, 2, 3, 4, 5, 6, 7) + \
#     np.random.normal(0, 1, 3 * pts)
# data = np.stack([xdata, ydata, zdata])
# popt = mvnaiveanalyze(data, 10, True)
# print(popt)

# plt.show()

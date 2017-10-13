
import numpy as np
import matplotlib.pyplot as plt
def naiveanalyze(data, fold=10, debug=False):
    # 5*30 - at least 150 tests recommended
    # assume polynomial fit, for now, but not order of equation
    # increment power until overfit (test error > by training error by significant amount)
    # scipy.optimize.curve_fit(f,xdata,ydata) <-allows initial guess
    # ydata = f(xdata, *params) + eps <- assumption
    # or numpy.polyfit(x,y,deg) <-easiest for now
    # TEST- Make function- generate random data, define bounds by what give original eq
    # overfit error = testerror - trainerror -compare slopes

    # split data set into training and test
    # np.random.shuffle shuffles columns
    print(np.shape(data))
    stop = False
    n = 1
    parray = []
    testArray = []
    resArray = []
    r2Array = []
    prevOverfit = np.Inf
    while not(stop):
        np.random.shuffle(data)
        splitdata = np.array(np.array_split(data, fold))
        foldOverMax = 0.0
        foldOverMin = np.Inf
        for f in range(fold):

            # testdata = data[:len(data)/fold,:]
            # traindata = data[len(data)/fold:,:]
            # cross validate by shuffling

            error = 0

            testdata = splitdata[f]
            traindata = np.concatenate(
                splitdata[np.arange(len(splitdata)) != f])
            p = np.polyfit(traindata[:, 0], traindata[:, 1], n, None, True)
            # equation from polynomial form. I guess I'll need this anyway.
            residuals = p[1]
            # print(residuals)

            N = len(testdata)
            # pbest = np.poly1d(0)
            resVals = []
            for i in range(0, N):
                res = (np.polyval(p[0], testdata[i, 0]) - testdata[i, 1])
                resVals.append(res)
                error += (res)**2
                # normalize do I divide by the original value here? Nah...

            errNorm = error / N
            foldOverfit = abs(residuals / len(traindata) - errNorm)
            # print(foldOverfit)
            if foldOverfit > foldOverMax:  # worst case/most overfit
                foldOverMax = foldOverfit

            if foldOverfit < foldOverMin:  # most generalizeable
                foldOverMin = foldOverfit
                bestRes = resVals
                bestTest = testdata
                # yhat = np.polyval(p[0], testdata[i, 0])
                y = testdata[:,1]
                ybar = np.sum(testdata[:, 1]) / N
                ssres = error
                # ssreg = np.sum((yhat-ybar)**2)
                sstot = np.sum((y - ybar)**2)
                r2 = 1 - ssres / sstot
                pbest = p[0]

                # save data for r**2 value
        parray.append(pbest)
        testArray.append(bestTest)
        resArray.append(bestRes)
        r2Array.append(r2)
# foldOverMax += foldOverfit #average case
# print(pbest)
# print(overfit) this sometimes works, sometimes doesn't
# instead going to check when test error increases
#        pbest /= 5
        # print(pbest)

# testdata = data[:len(data)/fold,:] #Random
#       traindata = data[len(data)/fold:,:]
#        error = 0
#       p=np.polyfit(traindata[:,0], traindata[:,1], n, None, True)
# equation from polynomial form. I guess I'll need this anyway.
#        residuals = p[1]
# print(residuals)
#        N = len(testdata)
# for i in range(0,N):
#          res = (np.polyval(p[0],testdata[i,0]) -  testdata[i,1])
# resMat[i,f]= res
#          error += (res)**2
# normalize do I divide by the original value here? I will not for now...
#        errNorm = berror/N
#        foldOverMax = abs(residuals/len(traindata) - errNorm)
# parray.append(p[0])

        # this constant is arbitrary
        if (prevOverfit != np.Inf) and (foldOverMax - prevOverfit) > -.4 * prevOverfit:
            stop = True
        n += 1  # increment polynomial
        prevOverfit = foldOverMax

    if debug:
        # pass#plot stuff here, and run loop a few more times to be sure
        Xplot = np.linspace(min(data[:, 0]), max(data[:, 0]), 100)
        if len(testArray) > 2:
            
            # plt.figure(1)
            plt.subplot(231)
            plt.plot(testArray[-3][:, 0], testArray[-3][:, 1], 'bo',
                     Xplot, np.polyval(parray[-3], Xplot), 'k--')
            plt.title('Order:%d' % (len(parray[-3])-1))
            plt.ylabel('Y')
            plt.xlabel('X')

        plt.subplot(232)
        plt.plot(testArray[-2][:, 0], testArray[-2][:, 1], 'bo',
                 Xplot, np.polyval(parray[-2], Xplot), 'k--')
        plt.title('Order:%d' % (len(parray[-2])-1))
        plt.ylabel('Y')
        plt.xlabel('X')

        plt.subplot(233)
        plt.plot(testArray[-1][:, 0], testArray[-1][:, 1], 'bo',
                 Xplot, np.polyval(parray[-1], Xplot), 'k--')
        plt.title('Order:%d' % (len(parray[-1])-1))
        plt.ylabel('Y')
        plt.xlabel('X')

        if len(testArray) > 2:
            plt.subplot(234)
            plt.plot(testArray[-3][:, 0], resArray[-3], 'rx')
            plt.title('r**2 = %.2f' % (r2Array[-3]))
            plt.ylabel('Y')
            plt.xlabel('X')

        plt.subplot(235)
        plt.plot(testArray[-2][:, 0], resArray[-2], 'rx')
        plt.title('r**2 = %.2f' % (r2Array[-2]))
        plt.ylabel('Y')
        plt.xlabel('X')

        plt.subplot(236)
        plt.plot(testArray[-1][:, 0], resArray[-1], 'rx')
        plt.title('r**2 = %.2f' % (r2Array[-1]))
        plt.ylabel('Y')
        plt.xlabel('X')
        plt.subplots_adjust(top=0.90, bottom=0.1, left=0.15, right=0.90,
                            hspace=0.49, wspace=0.7)
        plt.show()
    return parray[-2]
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


# naive analyze test
# import numpy as np
# import matplotlib.pyplot as plt
# ptest = np.array([ .8,-.30, .40,-.8,0 ,-.5 ])
# pts = 300
# under = 0
# over = 0
# for q in range(1000):
#     noise = np.random.normal(0, 5, pts)
#     x = [np.linspace(0.0, 15.0, pts)]
#     y = np.polyval(ptest, x) + noise
#     data = np.concatenate((x, y), axis=0).T
#     p = naiveanalyze(data, 10,True)
#     if len(p) < len(ptest):
#         under += 0.001
#     if len(p) > len(ptest):
#         over += 0.001
#     plt.show()
# print((under, over))

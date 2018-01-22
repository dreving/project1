import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


'''
Set of functions used in splitting Hysteresis Curves based
on Support Vector Machines
'''


# create Support Vector Machine
def build(riseData, fallData, C=100000, gamma=20):
    trainData = np.vstack((riseData, fallData))
    scaler = StandardScaler()
    # data works better when scaled to range of 1
    trainData = scaler.fit_transform(trainData)
    trainLabels = np.hstack(
        (-1 * np.ones(len(riseData)), np.ones(len(fallData))))
    clf = SVC(C=C, gamma=gamma, kernel='rbf',)
    clf.fit(trainData, trainLabels)
    return (clf, scaler)


# label data into rising and falling
def label(clf, scaler, fullData):
    fullData = scaler.transform(fullData)
    fullLabels = clf.predict(fullData)
    # print(np.shape(fullLabels))
    return fullLabels


# make two data sets (rising and falling) based on labels
def split(data, labels):
    data = data[np.argsort(labels)]
    # x + y = len
    # x - y = sum
    # x = len + sum / 2
    # the line below is the solution for the system of equations
    # stating how many are in each label, assuming the labels are -1 and 1
    split = int((len(labels) + sum(labels)) / 2)
    split = len(labels) - split
    riseData = data[:split, :]
    fallData = data[split:, :]
    return (riseData, fallData)

# same as labels simplified polynomial boundary as opposed to
# support vector machine


def qlabel(boundP, fullData):
    fullLabels = -1 * np.zeros((len(fullData[:, 0],)))
    for i in range(len(fullData[:, 0])):
        if np.polyval(boundP, fullData[i, 0]) < fullData[i, -1]:
            fullLabels[i] = 1
        elif np.polyval(boundP, fullData[i, 0]) >= fullData[i, -1]:
            fullLabels[i] = -1
    return fullLabels


# convert map based on support vector machine into polynomial of boundary
#  between upper and lower curves
def simplify(clf, scaler, convert=True, boundXL=4, test=None):
    # brake commands to consider
    x_min = -5.0
    x_max = 105.0
    # torque values to consider
    y_min = 1
    y_max = 120.0
    # also works for current values instead of torque
    if not(convert):
        y_max = 10.0

    # make dot grid of map and assign values
    XX, YY = np.mgrid[x_min:x_max:400j, y_min:y_max:400j]
    data = np.c_[XX.ravel(), YY.ravel()]
    sData = scaler.transform(data)
    Z = clf.decision_function(sData)

    # Put the result into a color plot
    Z = Z.reshape(XX.shape)
    fig = plt.figure()
    plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
    plt.contour(XX, YY, Z, colors=['k', 'k', 'k'],
                linestyles=['--', '-', '--'], levels=[-.5, 0, .5])

    # Values near zero form the boundary
    # Since there are many outlier points that equal zero, only
    # points between these two parallel lines are considered
    if convert:
        m = 110 / 90
        b1 = 15
        b2 = -25
    else:
        m = .1
        b1 = -.75
        b2 = -1.5

    boundpts = np.multiply((abs(Z) < 0.10), (-b1 < m * XX - YY)) > 0
    boundpts = np.multiply(boundpts, (-b2 > m * XX - YY)) > 0
    Xpts = XX[boundpts]
    Ypts = YY[boundpts]

    # plot boundary
    plt.plot(Xpts, Ypts, 'g^')
    scopeLinspace = np.linspace(x_min, x_max)
    scope1 = scopeLinspace * m + b1
    scope2 = scopeLinspace * m + b2
    plt.plot(scopeLinspace, scope1, 'k--')
    plt.plot(scopeLinspace, scope2, 'k--')
    if test is not None:
        plt.title(test)
    # plt.show()
    boundData = np.vstack((Xpts, Ypts))

    # fit polynomial based on boundary points
    p = np.polyfit(boundData[0, :], boundData[-1, :], boundXL)
    return p

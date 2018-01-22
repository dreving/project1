import numpy as np
import pickle
import matplotlib.pyplot as plt


def simplify(clf, scaler, convert=True, boundXL=4,test=None):
    x_min = -5.0
    x_max = 105.0
    y_min = 1
    y_max = 120.0
    if not(convert):
        y_max = 10.0

    XX, YY = np.mgrid[x_min:x_max:400j, y_min:y_max:400j]
    # scale here brah
    data = np.c_[XX.ravel(), YY.ravel()]
    sData = scaler.transform(data)
    Z = clf.decision_function(sData)

    # Put the result into a color plot
    Z = Z.reshape(XX.shape)
    fig = plt.figure()
    plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
    plt.contour(XX, YY, Z, colors=['k', 'k', 'k'],
                linestyles=['--', '-', '--'], levels=[-.5, 0, .5])
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
    # print(boundpts)
    Xpts = XX[boundpts]
    Ypts = YY[boundpts]
    plt.plot(Xpts, Ypts, 'g^')
    scopeLinspace = np.linspace(x_min, x_max)
    scope1 = scopeLinspace * m + b1
    scope2 = scopeLinspace * m + b2
    plt.plot(scopeLinspace, scope1, 'k--')
    plt.plot(scopeLinspace, scope2, 'k--')
    if test is not None:
        plt.title(test)
    plt.show()
    boundData = np.vstack((Xpts, Ypts))
    # p= analyze(boundData.T,4,True)
    p = np.polyfit(boundData[0, :], boundData[-1, :], boundXL)
    with open('data/' + 'boundP' + '.pickle', 'wb') as f:
        pickle.dump(p, f)
    return p

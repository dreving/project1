import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler


def build(riseData, fallData):
    trainData = np.vstack((riseData, fallData))
    scaler = StandardScaler()
    trainData = scaler.fit_transform(trainData)
    trainLabels = np.hstack(
        (-1 * np.ones(len(riseData)), np.ones(len(fallData))))
    print(np.shape(trainData))
    print(np.shape(trainLabels))
    clf = SVC(C=10,gamma=40, kernel='rbf', degree=1,)# cache_size=7000)
    #C100000 G40 Best So far for rbf
    #C10 #G40 for x y
    clf.fit(trainData, trainLabels)
    return (clf, scaler)


def label(clf, scaler, fullData):
    fullData = scaler.transform(fullData)
    fullLabels = clf.predict(fullData)
    # print(np.shape(fullLabels))
    return fullLabels


def split(data, labels):
    data = data[np.argsort(labels)]
    # x + y = len
    # x - y = sum
    # x = len + sum / 2
    split = int((len(labels) + sum(labels)) / 2)
    print(split)
    riseData = data[:split]
    fallData = data[split:]
    return (riseData, fallData)

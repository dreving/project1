import numpy as np
from sklearn.svm import SVC


def build(riseData, fallData):
    trainData = np.vstack((riseData, fallData))
    trainLabels = np.hstack(
        (-1 * np.ones(len(riseData)), np.ones(len(fallData))))
    print(np.shape(trainData))
    print(np.shape(trainLabels))
    clf = SVC(kernel='poly', degree=2)
    clf.fit(trainData, trainLabels)
    return clf


def label(clf, fullData):
    fullLabels = clf.predict(fullData)
    print(np.shape(fullLabels))
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

import pickle
import numpy as np


def export(fname):
    with open('data/' + fname + '.pickle', 'rb') as g:
        (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
    print(riseXL)
    print(p1)
    # print(np.shape(sVs)) 74 Support Vectors
    # linearApprox = None
    # scalerMean = scaler.mean
    # scalerScale = scaler.scale
    # RisePP=None
    # RiseDP=None
    # FallPP=None
    # FallDP=None


export('BackupController')

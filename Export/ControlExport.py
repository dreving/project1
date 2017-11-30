import pickle
import numpy as np


def export(fname, boundfname):
    with open('data/' + fname + '.pickle', 'rb') as g:
        (clf, scaler, p1, riseXL, p2, fallXL) = pickle.load(g)
    with open('data/' + boundfname + '.pickle', 'rb') as g:
        boundP = pickle.load(g)
    print('Coefficients Listed in Ascending Order C[0] + C[1]* X^1 + ...')
    print('Boundary Inequality Function: Torque = f(Command Percentage)')
    print('If Present Torque > f(present Command), use Upper Curve, else Lower Curve')
    print('Boundary Coefficients Are:')
    print(boundP[::-1])
    print('Command Calculation Functions: Command = g(Torque)')
    print('Lower Hysteresis Curve Coefficents Are:')
    print(p1[:riseXL])
    print('Lower Hysteresis Derivative Coefficents Are:')
    c2 = [0]
    c2.extend(p1[riseXL:])
    print(c2)
    print('Upper Hysteresis Curve Coefficents Are:')
    print(p2[:fallXL])
    print('Upper Hysteresis Derivative Coefficents Are:')
    c4 = [0]
    c4.extend(p2[fallXL:])
    print(c4)
    # print(np.shape(sVs)) 74 Support Vectors
    # linearApprox = None
    # scalerMean = scaler.mean
    # scalerScale = scaler.scale
    # RisePP=None
    # RiseDP=None
    # FallPP=None
    # FallDP=None


export('Controller','boundP')

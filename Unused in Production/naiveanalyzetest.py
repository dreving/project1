# naive analyze test
import numpy as np
import matplotlib.pyplot as plt
from mvnaiveanalyze import mvnaiveanalyze as analyze

def gf(data, *args, **kwargs):
    val = args[0]
    # global xParamLength
    xPL = kwargs.get('xPL', None)
    # print(xPL)
    for i in range(1, len(args)):
        i // xPL
        # coefficients of ascending degree
        val += args[i] * data[int(i >= xPL),

                              :]**(int(i >= xPL) + (i) % xPL)
    return val


pts = 300
xParamLength = 3
xdata = np.repeat(np.linspace(0.0, 1.0, pts), 3)
ydata = np.linspace(0.0, 3.0, 3 * pts)

zdata = gf(np.stack([xdata, ydata]), 1, 2, 3, 4, 5, xPL= xParamLength) + \
    np.random.normal(0, 1, 3 * pts)
data = np.stack([xdata, ydata, zdata]).T
print(np.shape(data))
popt = analyze(data, 10, True)
print(popt)

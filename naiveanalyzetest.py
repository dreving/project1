#naive analyze test
import numpy as np
ptest = np.array([2.0,3.0,4.0])
noise = np.random.normal(0,.1,150)
x = [np.linspace(0.0,149.0,150)]
y = np.polyval(ptest,x) + noise
data = np.concatenate((x, y), axis=0).T
print(data)
p = naiveanalyze(data, 5,True)
print(p)

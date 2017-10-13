import numpy as np

def itoT(i):
	T = -120.941 + 0.0111358 * np.sqrt(40160000 * i + 90000000)
	return T



print(itoT(.65))
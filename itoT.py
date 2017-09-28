import math


def itoT(i):
    T = -87.8125 + .1804 * math.sqrt(64000 * i + 152211)
    return T


# print(itoT(1.323))

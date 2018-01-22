import brake_implement as _brake
import time
import numpy as np

'''
Wrapper Class for the Nebula Python C extension
Can set torque and read input current
locates address automatically, so initialize last
to prevent attempted takeover of another device
'''


class Brake(object):
    def __init__(self):
        # extracts address of Nebula and Motion Controller within
        (self.Nb, self.Mc) = _brake.initNebula()
        # each unit of command = .1% rated current
        self.currentScale = 10
        self.fullCurrent = 2.1

    def setTorque(self, torque):
        try:
            torque = int(round(self.currentScale * torque))
            _brake.setTorque(self.Mc, torque)
            return True
        except:
            print("Brake Timeout")
            return False

    def readCurrent(self):
        try:
            return (_brake.readCurrent(self.Mc) / self.currentScale)
        except:
            print("Brake Timeout")
            return(np.nan)

    def close(self):
        self.setTorque(0)
        time.sleep(0.1)
        _brake.close(self.Nb, self.Mc)
        self.Mc = None
        self.Nb = None

# # for testing
# Nb = Brake()
# Nb.setTorque(50)
# time.sleep(5)
# print(Nb.readCurrent())
# print(Nb.readCurrent())
# print(Nb.readCurrent())
# Nb.close()

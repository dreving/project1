from arduino import Arduino
import time


class Ard_T(object):
    def __init__(self, address, pin):
        self.address = address
        self.pin = pin
        self.ard = Arduino(address)
        self.ard.output([])

    def readTemp(self):
        # Celcius
        V = int((self.ard).analogRead(self.pin)) * 3.3 / 1024
        T = (V - 1.250) / .005
        return T

    def isSafeTemp(self):
        crit = 32  # 32
        return (self.readTemp() < crit)

    def isStartTemp(self):
        crit = 27  # 27
        temp = self.readTemp()
        # print(temp)
        return (temp < crit)

    def isWarmTemp(self):
        crit = 27  # 32
        temp = self.readTemp()
        # print(temp)
        return (temp > crit)

# tc = Ard_T('COM3', 1)
# while(True):
#     print(tc.readTemp())
#     time.sleep(.5)

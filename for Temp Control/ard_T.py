from arduino import Arduino
import time

'''
Deprecated Class for using the Arduino for monitoring
the temperature of the model
'''


class Ard_T(object):
    def __init__(self, address, pin):
        self.address = address
        self.pin = pin
        self.ard = Arduino(address)
        self.ard.output([])
        self.aref = 3.3

    def readTemp(self):
        # Celcius
        V = int((self.ard).analogRead(self.pin)) * self.aref / 1024
        T = (V - 1.250) / .005
        return T

    def isSafeTemp(self):
        crit = 35  # 32
        temp = self.readTemp()
        return (temp < crit)

    def isStartTemp(self):
        crit = 25  # 27
        temp = self.readTemp()
        # print(temp)
        return (temp < crit)

    def isWarmTemp(self):
        crit = 15  # 32
        temp = self.readTemp()
        # print(temp)
        return (temp > crit)


# # These commented out lines print output for a sanity check on values,
# # gets stuck in infinite loop if left in
# tc = Ard_T('COM3', 1)
# while(True):
#     print(tc.readTemp())
#     time.sleep(.5)

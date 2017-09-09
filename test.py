
import brake
import time

Nb= brake.initNebula()
print(Nb)
brake.setTorque(Nb,0)
time.sleep(2)
brake.setTorque(Nb, 50)
time.sleep(2)
brake.setTorque(Nb, 0)



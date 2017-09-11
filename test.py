
import brake
import time
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
# print("starting")
# Nb, Mc = brake.initNebula()
# print((Nb,Mc))
# for i in range(100):
#     brake.setTorque(Mc, 0)
#     time.sleep(.2)
#     brake.setTorque(Mc, 50)
#     time.sleep(.2)
# brake.setTorque(Mc, 0)
# print('Stress Test Passed')
# brake.close(Nb, Mc)
# print('Motor Closed without Fault')
# print('All Tests Passed')


rc = RoboClaw('COM7', 0x80)
# Nb = brake.initNebula()
time.sleep(1)
CMF.setMotorSpeed(rc,90)
time.sleep(2)
CMF.stopMotor(rc)

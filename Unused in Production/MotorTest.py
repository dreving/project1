import time
from roboclaw import RoboClaw
import CalibrationMotorFunctions as CMF
import brake
rc = RoboClaw('COM7', 0x80)
Nb= brake.initNebula()
time.sleep(1)
#roboclaw1.drive_to_position_raw(motor=1, accel=0, speed=0, deccel=0, position=25, buffer=1)
#roboclaw1.stop_all()
#  print(roboclaw1.read_max_speed(1))
   # print(roboclaw1.read_position(1))



brake.setTorque(Nb, 50)
CMF.setMotorSpeed(rc,10)
time.sleep(.6)
print(CMF.readAvgCurrent(rc,10))
time.sleep(3)
CMF.stopMotor(rc)
brake.setTorque(Nb,0)
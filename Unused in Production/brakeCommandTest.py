# import brake
import ingenialink as il
from ingenialink import const, regs
import time
import CalibrationMotorFunctions as CMF
from roboclaw import RoboClaw


# Nb, Mc = brake.initNebula()
# brake.setTorque(Mc, 500)
# time.sleep(2)
# print(brake.readCurrent(Mc))
# brake.setTorque(Mc, 0)
# print('brake command sent')
# brake.close(Nb, Mc)
# print('brake closed')

# print(il.devices())
# rc = RoboClaw('COM7', 0x80)
print('connected to roboclaw')
net = il.Network('COM6',timeout=1000)
servo_ids = net.servos()
first_id = servo_ids[0]
servo = il.Servo(net, first_id,timeout=1000)
servo.mode = il.MODE_PT

servo.units_torque = il.UNITS_TORQUE_NATIVE
print(servo.read(regs.TORQUE_MAX))
print('Connected to Servo')
servo.enable(timeout=2000)
print('Servo Enabled')
time.sleep(10)
# CMF.setMotorSpeed(rc, CMF.compPWM(45, 0))
# time.sleep(.02)
servo.torque = 1000
# servo.wait_reached(timeout=1000)
print("Torque Set")
start = time.time()
print('Start Sleep')
while time.time() - start < 10:
	print('delay')
	time.sleep(0.02)
# time.sleep(10)
print(servo.torque)
print(servo.torque)
print(servo.torque)
# print(CMF.readAvgCurrent(rc, 2))
servo.torque = 0
# enable power stage


# disable power stage
servo.disable()
# CMF.stopMotor(rc)

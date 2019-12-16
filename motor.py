from RpiMotorLib import rpi_dc_lib
import time

ena = 22
in1 = 17
in2 = 27
in3 = 24
in4 = 23
enb = 25
'''
enb = 22
in3 = 17
in4 = 27
in1 = 24
in2 = 23
ena = 25
'''
motor1 = rpi_dc_lib.L298NMDc(in4, in3, enb, 1000, True, "motor_one")
motor2 = rpi_dc_lib.L298NMDc(in2, in1, ena, 1000, True, "motor_two")

def start():
	pass

def setM1Speed(x):
	if x < -100:
		x = -100
	if x > 100:
		x = 100
	if x < 0: # backward
		motor2.backward(-x)
		print("m1 back")
	else:
		motor2.forward(x)
		print("m1 for")
			
def setM2Speed(x):
	if x < -100:
		x = -100
	if x > 100:
		x = 100
	if x < 0: # backward
		motor1.backward(-x)
		print("m2 back")
	else:
		motor1.forward(x)
		print("m2 for")
			

def moveSteering(power, steering):
	pow1, pow2 = 0, 0
	if steering >= 0:
		pow1 = power
		pow2 = (-power * steering + 50*power)/50
	else:
		pow2 = power
		pow1 = (power * steering + 50*power)/50
	
	#pow1 = power + steering
	#pow2 = power - steering
	setM1Speed(pow1)
	setM2Speed(pow2)
	
	
def cleanup():
	motor1.cleanup(False)
	motor2.cleanup(False)

def forward(power):
	motor1.forward(power)
	motor2.backward(power)

def brake():
	motor1.brake()
	motor2.brake()


if __name__ == "__main__":

	motor1.forward(100)
	time.sleep(7)
	motor1.stop(0)
	motor2.forward(100)
	time.sleep(7)
	motor2.stop(0)
	#cleanup()
	exit()
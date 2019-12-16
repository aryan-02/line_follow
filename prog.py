import motor
import time
import RPi.GPIO as GPIO

motor.start();
motor.moveSteering(80, 10);
time.sleep(5);
GPIO.cleanup();
'''while 1:
	GPIO.setmode(GPIO.BCM)
	TRIG = 26
	ECHO = 19
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	GPIO.output(TRIG, True)
	time.sleep(0.0001)
	GPIO.output(TRIG, False)
	motor.start()
	start = 0
	end = 0
	while not GPIO.input(ECHO):
		start = time.time()

	while GPIO.input(ECHO):
		end = time.time()

	sig_time = end - start

	dist_cm = sig_time / 0.000058
	print("Distance:", dist_cm, "cm")

	time.sleep(1)'''
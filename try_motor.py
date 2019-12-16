import RPi.GPIO as GPIO
import time

m1a = 16
m1b = 18
ena = 15
m2a = 11
m2b = 13
enb = 22

GPIO.setmode(GPIO.BOARD)
for i in [m1a, m1b, m2a, m2b, ena , enb]:
	GPIO.setup(i, GPIO.OUT)

s1 = GPIO.PWM(ena, 1000)
s2 = GPIO.PWM(enb, 1000)
	
def start( x = 10 ):
	s1.ChangeDutyCycle(x)
	s2.ChangeDutyCycle(x)
	for i in [m1a, m2a]:
		GPIO.output(i, True)
	for i in [m1b, m2b]:
		GPIO.output(i, False)

def setM1Speed(x):
	if x < -100:
		x = -100
	if x > 100:
		x = 100
	if x >= 0:
		GPIO.output(m1a, True)
		GPIO.output(m1b, False)
		s1.ChangeDutyCycle(x)
	else:
		GPIO.output(m1a, False)
		GPIO.output(m1b, True)
		s1.ChangeDutyCycle(-x)

def setM2Speed(x):
	if x < -100:
		x = -100
	if x > 100:
		x = 100
	if x >= 0:
		GPIO.output(m2a, True)
		GPIO.output(m2b, False)
		s2.ChangeDutyCycle(x)
	else:
		GPIO.output(m2a, False)
		GPIO.output(m2b, True)
		s2.ChangeDutyCycle(-x)

def moveSteering(power, steering):
	p1 = power + steering
	p2 = power - steering
	setM1Speed(p1)
	setM2Speed(p2)
	
def cleanup():
	GPIO.output(m1a, False)
	GPIO.output(m1b, False)
	GPIO.output(m2a, False)
	GPIO.output(m2b, False)
	setM1Speed(0)
	setM2Speed(0)
	GPIO.cleanup()


		
	
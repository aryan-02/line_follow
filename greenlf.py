import picamera
import picamera.array
import time
import cv2
import numpy as np
import math
import motor
from constants import *
import RPi.GPIO as GPIO
import line_functions as line

motor.start()
cam = picamera.PiCamera()
res = (320, 176)
cam.resolution = res
rawCapture = picamera.array.PiRGBArray(cam, size=(res[0], res[1]))
time.sleep(0.1)

beg = time.time()
n = 0

left_count = 0
right_count = 0
u_count = 0

kP = 7
kD = 10
power = 100

trig1 = 20
echo1 = 16

trig2 =	26
echo2 = 19

for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	n+= 1
	distance = line.obstacle(trig1, echo1)
	image = frame.array
	green = line.green_func(image)
	if(distance < 15):
		#distance_r = line.obstacle_r(trig2, echo2)
		if(1):
			print("rescue")
		else:
			motor.moveSteering(-80, 0)
			time.sleep(1)
			motor.moveSteering(80, 40)
			time.sleep(2.5)
			motor.moveSteering(80, 0)
			time.sleep(1)
			motor.moveSteering(80, -40)
			time.sleep(3.5)
			motor.moveSteering(80, 0)
			time.sleep(1)
			print("obstacle")
	else:
		print(green)
		if(green != None):
			'''l = green.count("left")
			r = green.count("right")
			boo = False
			if((r-2) <= l <= (r+2)):
				boo = True
			else:
				boo = False'''
			if(len(green) == 0):
				line.black_func(image, kP, kD, power)
			elif(len(green) > 1 and "left" in green and "right" in green):
				motor.moveSteering(80, -100)
				time.sleep(5)
				print("u")
				# U turn
			elif(len(green) == 1 and green[0] == "left"):
				motor.moveSteering(80, -35)
				time.sleep(2)
				print("left")
				# LEFT turn
			elif(len(green) == 1 and green[0] == "right"):
				motor.moveSteering(80, 40)
				time.sleep(2)
				print("right")
				# RIGHT turn
		else:
			green = []
			line.black_func(image, kP, kD, power)
	
	cv2.imshow("Original", image)
	rawCapture.truncate(0)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		end = time.time()
		print(n / (end - beg), "FPS")
		motor.cleanup()
		GPIO.cleanup()
		break
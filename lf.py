import picamera
import picamera.array
import time
import cv2
import numpy as np
import math
import motor
from constants import *
import RPi.GPIO as GPIO

motor.start()
cam = picamera.PiCamera()
res = (640, 368)
cam.resolution = res
rawCapture = picamera.array.PiRGBArray(cam, size=(res[0], res[1]))
time.sleep(0.1)

x_last = 320
y_last = 150

for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	image = frame.array
	kernel = np.ones((3, 3), np.uint8)
	blackLine = cv2.inRange(image, (0, 0, 0), (50, 50, 50))
	blackLine = cv2.erode(blackLine, kernel, iterations=4)
	blackLine = cv2.dilate(blackLine, kernel, iterations=9)
	img, contours, heirarchy = cv2.findContours(blackLine.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
	if len(contours) > 0:
		#cv2.rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 3)
		# cv2.line(image, (x+(w//2), 0), (x + (w//2), 368), (255, 0, 0), 3)
		if len(contours) == 1:
			blackBox = cv2.minAreaRect(contours[0])
		else:
			candidates = []
			off_bottom = 0
			for cont_num in range(len(contours)):
				blackBox = cv2.minAreaRect(contours[cont_num])
				(x_min, y_min) , (w_min, h_min), ang = blackBox
				box = cv2.boxPoints(blackBox)
				(x_box , y_box) = box[0]
				if y_box > 400:
					off_bottom += 1
				candidates.append((y_box, cont_num, x_min, y_min))
			candidates.sort()
			if off_bottom > 1:
				candidates_off_bottom = []
				for cont_num in range(len(contours) - off_bottom, len(contours)):
					(y_highest, cont_highest, x_min, y_min) = candidates[cont_num]
					total_distance = ((x_min - x_last)**2 + (y_min - y_last)**2)**0.5
					candidates_off_bottom.append((total_distance, cont_highest))
				candidates_off_bottom.sort()
				(total_distance, cont_highest) = candidates_off_bottom[0]
				blackBox = cv2.minAreaRect(contours[cont_highest])
			else:
				(y_highest, cont_highest, x_min, y_min) = candidates[len(contours) - 1]
				blackBox = cv2.minAreaRect(contours[cont_highest])					
		(x_min, y_min), (w_min, h_min), ang = blackBox
		x_last = x_min
		y_last = y_min
		ang = int(ang)
		if ang < -45:
			ang += 90
		middle = res[0] // 2
		error = x_min - middle
		error = (error / 320) * 100
		box = cv2.boxPoints(blackBox)
		box = np.int0(box)
		cv2.drawContours(image, [box], 0, (0, 0, 255), 3)
		cv2.line(image, (int(x_min), 0), (int(x_min), 480), (0, 255, 0), 2)
		cv2.putText(image, str(ang) + "deg", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
		cv2.putText(image, str(error), (80, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		derivative = math.tan(math.radians(ang))
		steering = error * kP + derivative * kD
		motor.moveSteering(75, steering)
		cv2.putText(image, "Steer: " + str(steering), (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
		
	cv2.imshow("Original", image)
	rawCapture.truncate(0)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		GPIO.cleanup()
		break
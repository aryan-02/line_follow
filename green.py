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

def Reverse(tuples): 
    new_tup = tuples[::-1] 
    return new_tup 
    
for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	image = frame.array
	kernel = np.ones((3, 3), np.uint8)
	thresh_low = np.array([0, 100, 0])
	thresh_high = np.array([100, 255, 100])
	
	green_mask = cv2.inRange(image, thresh_low, thresh_high)
	green_mask = cv2.erode(green_mask, kernel, iterations=4)
	green_mask = cv2.dilate(green_mask, kernel, iterations=9)
	img_g, contours_g, heirarchy_g = cv2.findContours(green_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	#cv2.drawContours(image, contours_g, -1, (0, 255, 0), 3)
	
	print(len(contours_g))
	
	action = []
	for i in range(len(contours_g)):
		x,y,w,h = cv2.boundingRect(contours_g[i])
		cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
		lower_bands = 2
		higher_bands = 5
		black_threshhold = 100
		a = 2
				
		#LEFT LINE
		left_line = np.array([[y, x-a]])
		topl_current = (y, x-a)
		color_topl = image[topl_current]
		left_line_colors = np.array([color_topl])
		for a in range(lower_bands,higher_bands):
			for j in range(y+1, y+h):
				left_line = np.append(left_line, [[j, x-a]], axis=0)
				current_index = (j, x-a)
				current_color = image[current_index]
				left_line_colors = np.append(left_line_colors, [current_color], axis=0)
		left_line_colors = np.average(left_line_colors)
		
		#TOP LINE
		top_line = np.array([[y, x-a]])
		topltop_current = (y, x-a)
		color_topltop = image[topltop_current]
		top_line_colors = np.array([color_topltop])
		for a in range(lower_bands,higher_bands):
			for j in range(x+1, x+w):
				top_line = np.append(top_line, [[y-a, j]], axis=0)
				current_index = (y-a, j)
				current_color = image[current_index]
				top_line_colors = np.append(top_line_colors, [current_color], axis=0)
		top_line_colors = np.average(top_line_colors)
		
		#RIGHT LINE
		right_line = np.array([[y, x+w+a]])
		topr_current = (y, x+w+a)
		color_topr = image[topr_current]
		right_line_colors = np.array([color_topr])
		for a in range(lower_bands,higher_bands):
			for j in range(y+1, y+h):
				right_line = np.append(top_line, [[j, x+w+a]], axis=0)
				current_index = (j, x+w+a)
				current_color = image[current_index]
				right_line_colors = np.append(right_line_colors, [current_color], axis=0)
		right_line_colors = np.average(right_line_colors)
		
		#BOTTOM LINE
		bot_line = np.array([[y+h, x]])
		bot_current = (y+h, x)
		color_bot = image[bot_current]
		bot_line_colors = np.array([color_bot])
		for a in range(lower_bands,higher_bands):
			for j in range(x+1, x+w):
				bot_line = np.append(bot_line, [[y+h+a, j]], axis=0)
				current_index = (y+h+a, j)
				current_color = image[current_index]
				bot_line_colors = np.append(bot_line_colors, [current_color], axis=0)
		bot_line_colors = np.average(bot_line_colors)
		
		
		if(int(left_line_colors) < black_threshhold and int(top_line_colors) < black_threshhold):
			print("right")
			action.append("right")
		elif(int(right_line_colors) < black_threshhold and int(top_line_colors) < black_threshhold):
			print("left")
			action.append("left")
		else:
			print("Nahi chal raha")
		print(left_line_colors)
		print(top_line_colors)
		print(right_line_colors)
		print(bot_line_colors)
		print(action)
	
	
	cv2.imshow("Original", image)
	rawCapture.truncate(0)
	key = cv2.waitKey(1000) & 0xFF
	if key == ord('q'):
		GPIO.cleanup()
		break
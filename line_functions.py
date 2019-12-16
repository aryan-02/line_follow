import picamera
import picamera.array
import time
import cv2
import numpy as np
import math
import motor
import threading
from constants import *
import RPi.GPIO as GPIO

motor.start()
res = (320, 176)
time.sleep(0.1) 

x_last = res[0]//2
y_last = res[1]//2

last_steer = 0
# GREEN function	
def t_func(box):
	l, r, t, b = False, False, False, False
	print("box: ", box)
	for i in box:
		if(i[0] >= (res[0] - 10)):
			r = True
		elif(i[0] <= 10):
			l = True
		elif(i[1] <= 10):
			t = True
		elif(i[1] >= (res[1] - 10)):
			b = True
	if(b and t and r):
		return True
	elif(b and t and l):
		return True
	else:
		return False
def green_func(image):
	global a
	action = []
	kernel_g = np.ones((3, 3), np.uint8)		
	green_mask = cv2.inRange(image, thresh_low_green, thresh_high_green)
	green_mask = cv2.erode(green_mask, kernel_g, iterations=4)
	green_mask = cv2.dilate(green_mask, kernel_g, iterations=9)
	img_g, contours_g, heirarchy_g = cv2.findContours(green_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
	cv2.drawContours(image, contours_g, -1, (0, 255, 0), 3)
		
	print(len(contours_g))
	
	if(len(contours_g) > 0):
		#if(action == None")
		for i in range(len(contours_g)):
			x,y,w,h = cv2.boundingRect(contours_g[i])
			if((x + w + higher_bands) >= res[0] or (y + h + higher_bands) >= res[1]):
				break
			cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
			
					
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
			if(int(bot_line_colors) < black_threshhold):
				continue
			elif(int(left_line_colors) < black_threshhold and int(top_line_colors) < black_threshhold and int(bot_line_colors) > black_threshhold):
				action.append("right")
				print("r")
				print(action)
			elif(int(right_line_colors) < black_threshhold and int(top_line_colors) < black_threshhold and int(bot_line_colors) > black_threshhold):
				action.append("left")
				print("l")
				print(action)
			else:
				print("hello")
		return action
	elif(len(contours_g) == 0):
		action = []
		return action 	

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

# BLACK func
def black_func(image, kP, kD, power):
	global last_steer
	global x_last
	global y_last
	kernel = np.ones((3, 3), np.uint8)
	blackLine = cv2.inRange(image, thresh_low_black, thresh_high_black)
	blackLine = cv2.erode(blackLine, kernel, iterations=1)
	blackLine = cv2.dilate(blackLine, kernel, iterations=5)
	# find black contours
	img, contours, heirarchy = cv2.findContours(blackLine.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
	if len(contours) == 0:
		print("ok")
		#set_interval(motor.moveSteering(-80, 0), 1)
	elif len(contours) > 0:
		#cv2.rectangle(image, (x,y), (x+w, y+h), (0, 255, 0), 3)
		# cv2.line(image, (x+(w//2), 0), (x + (w//2), 368), (255, 0, 0), 3)
		if len(contours) == 1:
			blackBox = cv2.minAreaRect(contours[0])
		else:
			candidates = []
			off_bottom = 0 # Number of contours off bottom
			for cont_num in range(len(contours)):
				blackBox = cv2.minAreaRect(contours[cont_num])
				(x_min, y_min) , (w_min, h_min), ang = blackBox
				box = cv2.boxPoints(blackBox)
				(x_box , y_box) = box[0]
				if y_box > 175:
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
		box = cv2.boxPoints(blackBox)
		ang = int(ang)
		if ang < -45:
			ang += 90
		if w_min < h_min and ang > 0:
			ang = (90 - ang) * -1
		if w_min > h_min and ang < 0:
			ang = 90 + ang
		if(ang >= 80 or ang <= -80):
			ang = 0
		middle = res[0] // 2
		error = x_min - middle
		error = (error / middle) * 100
		box = cv2.boxPoints(blackBox)
		box = np.int0(box)
		cv2.drawContours(image, [box], 0, (0, 0, 255), 3)
		cv2.line(image, (int(x_min), 0), (int(x_min), 480), (0, 255, 0), 2)
		cv2.putText(image, str(ang) + "deg", (10*(res[0]//100), 30*(res[1]//100)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
		cv2.putText(image, str(error), (10*(res[0]//100), 60*(res[1]//100)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
		derivative = math.tan(math.radians(ang))
		steering = (error * kP)/3.2 + derivative * kD
		motor.moveSteering(power, steering)
		print("moving")
		cv2.putText(image, "Steer: " + str(steering), (10*(res[0]//100), 90*(res[1]//100)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
		return box

def obstacle(TRIG, ECHO):
	while 1:
		global start
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(TRIG, GPIO.OUT)
		GPIO.setup(ECHO, GPIO.IN)
		GPIO.output(TRIG, True)
		time.sleep(0.0001)
		GPIO.output(TRIG, False)
		#motor.start()
		start = 0
		end = 0
		while not GPIO.input(ECHO):
			start = time.time()

		while GPIO.input(ECHO):
			end = time.time()

		sig_time = end - start

		dist_cm = sig_time / 0.000058
		return dist_cm
		print("Distance:", dist_cm, "cm")

		GPIO.cleanup()
		time.sleep(1)
		
def obstacle_r(TRIG_R, ECHO_R):
	while 1:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(TRIG_R, GPIO.OUT)
		GPIO.setup(ECHO_R, GPIO.IN)
		GPIO.output(TRIG_R, True)
		time.sleep(0.0001)
		GPIO.output(TRIG_R, False)
		#motor.start()
		start_r = 0
		end_r = 0
		while not GPIO.input(ECHO_R):
			start_r = time.time()

		while GPIO.input(ECHO_R):
			end_r = time.time()

		sig_time_r = end_r - start_r

		dist_cm_r = sig_time_r / 0.000058
		return dist_cm_r
		print("Distance:", dist_cm_r, "cm")

		GPIO.cleanup()
		time.sleep(1)
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from utils.objcenter import ObjCenter
from utils.pid import PID
from utils.PCA9685 import PCA9685
import argparse
import signal
import sys
import cv2
import time

# define the range for the motors
servoRange = (-90, 90)

# function to handle keyboard interrupt
def signal_handler(sig, frame):
	# print a status message
	print("[INFO] You pressed `ctrl + c`! Exiting...")
	# disable the servos
	global pwm
	pwm.setServoPulse(0,0)
	pwm.setServoPulse(1,0)
	# exit
	sys.exit()

def obj_center(args, objX, objY, centerX, centerY):
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)
	# start the video stream and wait for the camera to warm up
	vs = VideoStream(usePiCamera=True, resolution=(640,480), framerate=50).start()
	time.sleep(2.0)
	# initialize the object center finder
	obj = ObjCenter(args["cascade"])
	# loop indefinitely
	while True:
		# grab the frame from the threaded video stream
		frame = vs.read()
		frame = cv2.flip(frame, 1)

		# calculate the center of the frame as this is where we will
		# try to keep the object
		(H, W) = frame.shape[:2]
		centerX.value = W // 2
		centerY.value = H // 2
		# find the object's location
		objectLoc = obj.update(frame, (centerX.value, centerY.value))
		((objX.value, objY.value), rect0, rect1) = objectLoc
		# extract the bounding box and draw it
		if rect0 is not None:
			(x0, y0, w0, h0) = rect0
			cv2.rectangle(frame, (x0, y0), (x0 + w0, y0 + h0), (0, 255, 0),
				2)
		if rect1 is not None:
			(x1, y1, w1, h1) = rect1
			cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0),
				2)
		# display the frame to the screen
		cv2.imshow("Pan-Tilt Eye Tracking", frame)
		cv2.waitKey(1)

def pid_process(output, p, i, d, objCoord, centerCoord):
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)
	# create a PID and initialize it
	p = PID(p.value, i.value, d.value)
	p.initialize()
	# loop indefinitely
	while True:
		# calculate the error
		error = centerCoord.value - objCoord.value
		# update the value
		output.value = p.update(error)
		
def in_range(val, start, end):
	# determine the input value is in the supplied range
	return (val >= start and val <= end)
	
def convert(degree):
	pulse = int((((degree + 90) * (2500 - 500)) / (90 + 90)) + 500)
	return pulse
	
def set_servos(pan, tlt):
	global pwm
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)
	# loop indefinitely
	while True:
		# the pan and tilt angles are reversed
		panAngle = -1 * pan.value
		tiltAngle = -1 * tlt.value
		# if the pan angle is within the range, pan
		if in_range(panAngle, servoRange[0], servoRange[1]):
			pwm.setServoPulse(0,convert(panAngle))
		# if the tilt angle is within the range, tilt
		if in_range(tiltAngle, servoRange[0], servoRange[1]):
			pwm.setServoPulse(1,convert(tiltAngle))

if __name__ == "__main__":
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--cascade", type=str, required=True,
		help="path to input Haar cascade for eye detection")
	#ap.add_argument("-e", "--eye", type=str, required=True,
		#help="path to input Haar cascade for eye detetection")
	args = vars(ap.parse_args())
	
	# start a manager for managing process-safe variables
	with Manager() as manager:
		# enable the servos
		pwm = PCA9685(0x40, debug=False)
		pwm.setPWMFreq(50)
		# set integer values for the object center (x, y)-coordinates
		centerX = manager.Value("i", 0)
		centerY = manager.Value("i", 0)
		# set integer values for the object's (x, y)-coordinates
		objX = manager.Value("i", 0)
		objY = manager.Value("i", 0)
		# pan and tilt values will be managed by independed PIDs
		pan = manager.Value("i", 0)
		tlt = manager.Value("i", 0)
		
		# set PID values for panning
		panP = manager.Value("f", 0.02) #0.02
		panI = manager.Value("f", 0.0002) #0.0002
		panD = manager.Value("f", 0.01) #0.01
		# set PID values for tilting
		tiltP = manager.Value("f", 0.07) #0.06-0.07
		tiltI = manager.Value("f", 0.0001) #0.0001-0.0002
		tiltD = manager.Value("f", 0.002) #0.002
		
		# we have 4 independent processes
		# 1. objectCenter  - finds/localizes the object
		# 2. panning       - PID control loop determines panning angle
		# 3. tilting       - PID control loop determines tilting angle
		# 4. setServos     - drives the servos to proper angles based
		#                    on PID feedback to keep object in center
		processObjectCenter = Process(target=obj_center,
			args=(args, objX, objY, centerX, centerY))
		processPanning = Process(target=pid_process,
			args=(pan, panP, panI, panD, objX, centerX))
		processTilting = Process(target=pid_process,
			args=(tlt, tiltP, tiltI, tiltD, objY, centerY))
		processSetServos = Process(target=set_servos, args=(pan, tlt))
		# start all 4 processes
		processObjectCenter.start()
		processPanning.start()
		processTilting.start()
		processSetServos.start()
		# join all 4 processes
		processObjectCenter.join()
		processPanning.join()
		processTilting.join()
		processSetServos.join()
		# disable the servos
		pwm.setServoPulse(0,0)
		pwm.setServoPulse(1,0)
		

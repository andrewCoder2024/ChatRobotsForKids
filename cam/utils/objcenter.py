import imutils
import cv2

class ObjCenter:
	def __init__(self, haarPath):
		# load OpenCV's Haar cascade face detector
		self.facedetector = cv2.CascadeClassifier(haarPath)
		#self.eyedetector = cv2.CascadeClassifier(eyehaarPath)
	def update(self, frame, frameCenter):
		# convert the frame to grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		cv2.equalizeHist(gray, gray);
		# detect all faces in the input frame
		rects = self.facedetector.detectMultiScale(gray, scaleFactor=1.05,
			minNeighbors=9, minSize=(30, 30),
			flags=cv2.CASCADE_SCALE_IMAGE)
		
		# check to see if a face was found
		if len(rects) > 0:
			# extract the bounding box coordinates of the face and
			# use the coordinates to determine the center of the
			# face
			(x0, y0, w0, h0) = rects[0]
			eyeX = int(x0 + (w0 / 2.0))
			eyeY = int(y0 + (h0 / 2.0))
			if len(rects) > 1:
				(x1, y1, w1, h1) = rects[1]
				#eyeX = int(x0 + w0 + ((x1 - x0 + w0) / 2.0))
				eyeY = int(y0 + h0 + ((y1 - y0 + h0) / 2.0))
				return ((eyeX, eyeY), rects[0], rects[1])
			# return the center (x, y)-coordinates of the face
			return ((eyeX, eyeY), rects[0], None)
		# otherwise no faces were found, so return the center of the
		# frame
		return (frameCenter, None, None)

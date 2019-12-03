
from imutils.video import VideoStream
import numpy as np
import cv2
import time


# PiClopse Video Capture object
class PCVideoCapture:
	def __init__(self,camnum):
		self.cam = camnum
		#self.vc = cv2.VideoCapture(self.cam)
		self.vs = VideoStream(self.cam).start()

class PCVideoRecord:
	def __init__(self):
		self.file = None

class PCConfiguration:
	def __init__(self):
		self.confmap = None




#A
#class Cy
#class CyVideoCapture( stream ):objectobjectobj

vc = PCVideoCapture( 0 )
print( "[INFO] VideoCapture initialized. Pausing for cam to stabilize" )

time.sleep(5.0)
print( "[INFO] Cam stabilized... Begining main processing loop" )

processing = True
i = 0

while( processing ):
	print( "[DEBUG] Loop iteration ", i )
	time.sleep(1.0)
	i = i + 1
	if i > 10:
		processing = False



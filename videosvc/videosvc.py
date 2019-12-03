
from imutils.video import VideoStream
import numpy as np
import cv2
import time
from threading import Thread
import imutils


# PiClopse Video Capture object

# PCVideoCapture Object - Used to capture the raw video stream from webcam
class PCVideoCapture(Thread):
	#def __init__(self,camnum):
	# Initialization and creation of baseline configuration values for stream
	def __init__(self):
		#self.cam = camnum
		self.curframe = None
		self.cam = 0
		#self.vs = VideoStream(self.cam)
		self.vs = cv2.VideoCapture(self.cam)
		self.running = False
		fourcc = cv2.VideoWriter_fourcc(*'X264')
		self.tmpraw = cv2.VideoWriter('tout.mov',fourcc, 20.0, (640,480))
		Thread.__init__(self)

	# Function to start the separate thread for video capture
	def start(self):
		self.running = True
		Thread.start(self)

	# Shutdown the capture thread
	def stop(self):
		self.running = False

	# Run loop for the video capture
	def run(self):
		while self.running:
			#print( "[DEBUG] VideoCap - In Thread Running" )
			# Minimal pause to avoid hogging CPU
			time.sleep(0.01)
			# Read the frame from the stream and store locally
			ret,tframe = self.vs.read()
			self.curframe = tframe
			#self.tmpraw.write(tframe)

	# Function used to pull the current frame to any component interested
	def read(self):
		return( self.curframe )



# Class to actually store the video in a file (not implemented yet - in main loop for now)
class PCVideoRecord:
	def __init__(self):
		self.file = None

# Pull initial configuration information (not implemented yet)
#   Should be able to repull on signal or via periodic polling
class PCConfiguration:
	def __init__(self):
		self.confmap = None

# Primary detector class with deviation and thresholding logic
class PCDetector:

	# Declare variables for this class
	bgframe = None       # BG Composite frame to compare against
	combineratio = 0.2   # Weighting of FG vs BG image when comparing
	threshold = 0.5      # Movement threshold
	tmpthresh = None

	# Initialize detector object
	def __init__(self):
		print( "[DEBUG] Initializing PiClops Detector" )
		self.threshold = 0.5
		#self.combineratio = 0.2
		self.combineratio = 0.5
		self.bgframe = None
		fourcc = cv2.VideoWriter_fourcc(*'X264')
		self.tmpthresh = cv2.VideoWriter('thresh.mov',fourcc, 20.0, (640,480),False)
		print( "[DEBUG] PiClops Detector initilaization complete" )

	# Update called with each new frame
	def update(self, newframe):
		if self.bgframe is None:
			print( "[DEBUG] Copying in bgframe" )
			self.bgframe = newframe.copy().astype("float")
			return

		else:
			print( "[DEBUG] Execution of combination logic" )
			cv2.accumulateWeighted(newframe, self.bgframe, self.combineratio)

	# Compare new image (frame) vs background image (frame)
	def checkdiff(self, newframe):
		# Pull difference between two frames and store temoraririly
		diff = cv2.absdiff(self.bgframe.astype("uint8"), newframe)

		# Thresholding logic to evaluate the difference between before image and after image
		thresh = cv2.threshold(diff, self.threshold*100, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.erode(thresh, None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=2)

		# Pull the contours / differences between frames. Theorietically minimal change == 0
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)

		if self.tmpthresh is not None:
			self.tmpthresh.write(thresh)

		print( "[DEBUG] Image analyzed. Number of contours in diff: ", len(contours))
		#for c in countours:
		#	print( )



# Begin MAIN program logic

# Initialize local PiClops objects
vc = PCVideoCapture(  )
det = PCDetector()

print( "[INFO] VideoCapture initialized. Pausing for cam to stabilize" )
# Fire up capture thread so pulling of new camera frames won't be blocked during processing
vc.start()

# Give the webcam time to auto-adjust aperture and light levels
time.sleep(5.0)
print( "[INFO] Cam stabilized... Begining main processing loop" )

# Loop variable indicating we're currently in-flight. Signal interrupts to set processing - False and exit
processing = True
i = 0

# Transform function for video encoding
fourcc = cv2.VideoWriter_fourcc(*'X264')

# Writer that stores the video file
raw = cv2.VideoWriter('output.mov',fourcc, 20.0, (640,480))
# Let's attempt to store the transient states as well - can be removed later
fggs = cv2.VideoWriter('outputfggs.mov',fourcc, 20.0, (640,480),False)
bggs = cv2.VideoWriter('outputbggs.mov',fourcc, 20.0, (640,480),False)

# Main processing loop
#    Grab the latest frame from the videostream
#    Run it through the motion detector
#    If we satisfy the thresholding, record the video
#       Else, stop recording and close the file
while( processing ):
	print( "[DEBUG] Loop iteration ", i )
	# Grab the frame from the stream
	frame = vc.read()

	# Leverage gray scale for our image comparison
	gsframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# Blur/fuzz the image a bit to eliminate background noise
	gsframe = cv2.GaussianBlur(gsframe, (7, 7), 0)

	# Update the background image with the composite view
	det.update( gsframe )
	# Compare background and foreground images
	#    note: Should checkdiff be before update
	#          Probably OK since it's a composite frame
	det.checkdiff( gsframe )
	#print( "[DEBUG] Frame info: ", frame.get(3) )

	# Store the image information - need to add check that we've triggered motion
	raw.write(frame)
	#fggs.write(np.uint8(gsframe))
	#bggs.write(np.uint8(det.bgframe))

	# Future we won't need this - just for testing purposes to limit time we're recording and exit gracefully
	#time.sleep(0.2)
	#time.sleep(0.2)
	i = i + 1
	#if i > 25:
	if i > 500:
		processing = False


# Done with the loop, shut down thread and close down files
vc.stop()
raw.release()
fggs.release()
bggs.release()



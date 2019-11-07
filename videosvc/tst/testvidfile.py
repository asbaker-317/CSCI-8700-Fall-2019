#!/usr/bin/python3


import cv2
import numpy as np
import yaml


settings = yaml.full_load(open('../settings.yaml'))

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(1)

# Define the codec and create VideoWriter object
#This works on windows - Not on Mac
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = cv2.VideoWriter('output.mov',fourcc, 20.0, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        #cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()


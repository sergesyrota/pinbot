from collections import deque
import numpy as np
import argparse
import imutils
import cv2

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (0, 0, 10)
greenUpper = (255, 40, 250)
pts = deque(maxlen=255)

# Webcam
#camera = cv2.VideoCapture(0)
#camera.set(3, 320) # width
#camera.set(4, 240) # height
#camera.set(5, 30.0) # fps
# Video file
#camera = cv2.VideoCapture("/Users/sergeysyrota/opencv/Pinball-playing/gameplay.mp4")
camera = cv2.VideoCapture("/Users/sergeysyrota/opencv/Pinball-playing/multi-ball.mov")
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

#skip first some frames
# 350 - for south park
# 3700 - single-ball action for a little bit
#for i in xrange(1,3700):
#    camera.read()

# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if not grabbed:
        break
    
    # resize the frame, blur it, and convert it to the HSV
    # color space
    #frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
      
    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = fgbg.apply(frame)
    #mask=cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=1)
    (_, cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 80:
            continue
            
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show original on the screen
    cv2.imshow("Original", frame)
    # show the frame to our screen
    cv2.imshow("Frame", mask)
    key = cv2.waitKey(1) & 0xFF
        
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

#!/usr/bin/env python

from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import sys
import os
from communication import arduino

parser = argparse.ArgumentParser()
parser.add_argument('-src', '--src', help='Input video', required=True)
parser.add_argument('-out', '--out', help='Output video', required=False)
parser.add_argument('-port', '--port',
                    help='Serial communication port for Arduino',
                    required=False)
parser.add_argument('-stage', '--stage',
                    help='''Override stages of the game (right flipper, left
                        flipper, gameplay) by supplying frame numbers (100,
                        500, 1000)''',
                    required=True)
args = parser.parse_args()

stages = map(int, args.stage.split(','))
print stages

# list of tracked points
pts = deque(maxlen=255)

# Webcam
# camera = cv2.VideoCapture(0)
# camera.set(3, 320) # width
# camera.set(4, 240) # height
# camera.set(5, 30.0) # fps

# Video file
camera = cv2.VideoCapture(args.src)
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

# Saving output for further analysis, if output is specified
if (args.out):
    os.remove(args.out)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(args.out, fourcc, 10.0, (640, 426))

# keep looping
frameNumber = 0
currentStage = -1
while True:
    frameNumber = frameNumber+1
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if not grabbed:
        break

    print("%d =========================" % frameNumber)
    # resize the frame, blur it, and convert it to the HSV
    # color space
    # frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = fgbg.apply(blurred)
    # mask=cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=1)
    (_, cnts, _) = cv2.findContours(mask.copy(),
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 80:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print('%d, %d; size: %d' % (x+w/2, y+h/2, cv2.contourArea(c)))

    # Show original on the screen
    cv2.imshow("Original", frame)
    # show the frame to our screen
    cv2.imshow("Frame", mask)
    if (args.out):
        out.write(frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
out.release()
cv2.destroyAllWindows()

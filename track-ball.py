#!/usr/bin/env python

from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import sys
import os
from datetime import datetime
from communication.arduino import Arduino

parser = argparse.ArgumentParser()
parser.add_argument('--src', help='Input video', required=True)
parser.add_argument('--out', help='Output video', required=False)
parser.add_argument('--port',
                    help='Serial communication port for Arduino',
                    default='/dev/null',
                    required=False)
parser.add_argument('--stage',
                    help='''Override stages of the game (right flipper, left
                        flipper, gameplay) by supplying frame numbers (100,
                        500, 1000)''',
                    required=True)
parser.add_argument('--cooldown',
                    help='''Cooldown time after flipper pressed
                        (to prevent feedback loops and not to overheat coil)
                        Has to be greater than time flipper will stay pressed.''',
                    default=300,
                    required=False)
args = parser.parse_args()


def getSecondsString(timedelta):
    return "{}.{:03d}".format(timedelta.seconds, timedelta.microseconds/1000)


class State:
    # timestamp of program start
    time_start = 0
    # Timestamp of when we finished processing the frame
    time_processing_ended = 0
    # Timestamp of when we finished capturing a frame
    time_captured = 0
    # Timestamp of when command to press button was last sent
    # Needed to track flipper location for training and to prevent feedback loops from own movement
    time_press_a = 0
    time_press_b = 0

    flipper_a_trained = False
    flipper_b_trained = False

    # Tracking frame numbers, possibly useful in training on video...
    frame_number = 0

stages = map(int, args.stage.split(','))
print stages

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

# Keep track of current state in this object
state = State()
# arduino = Arduino(args.port)
state.time_start = state.time_processing_ended = datetime.now()
currentStage = -1
while True:
    state.frame_number = state.frame_number+1
    # grab the current frame
    (grabbed, frame) = camera.read()
    state.time_captured = datetime.now()
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if not grabbed:
        break

    print("%d =========================" % state.frame_number)
    # Detection works better on a blurred frame
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    mask = fgbg.apply(blurred)
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

    # Processing END timeframe
    cv2.putText(frame, getSecondsString(state.time_captured-state.time_start),
                (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Capture: {}s".format(getSecondsString(state.time_captured-state.time_processing_ended)),
                (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    # This needs to be assigned after ^ capture time calculation, so we can use the same timer.
    state.time_processing_ended = datetime.now()
    cv2.putText(frame, "Processing: {}s".format(getSecondsString(state.time_processing_ended-state.time_captured)),
                (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    # Show original on the screen
    cv2.imshow("Original", frame)
    # show the frame to our screen
    # cv2.imshow("Frame", mask)
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

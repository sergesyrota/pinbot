#!/usr/bin/env python

from __future__ import print_function
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import sys
import os
from datetime import datetime, timedelta
from communication.arduino import Arduino
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('--src', help='Input video', required=True)
parser.add_argument('--out', help='Output video', required=False)
parser.add_argument('--show', help='Show live video (with annotations) on the screen in real time',
                    required=False, const=True, action='store_const')
parser.add_argument('--port',
                    help='Serial communication port for Arduino',
                    default='/dev/null',
                    required=False)
parser.add_argument('--cooldown',
                    help='''Cooldown time (milliseconds) after flipper pressed
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
    time_press_a = datetime.now()
    time_press_b = datetime.now()

    flipper_a_trained = False
    flipper_b_trained = False
    # Set this to True after a frame with flipper contour was sent. Reverse to False when we press flipper button.
    flipper_countour_sent = False

    # Tracking frame numbers, possibly useful in training on video...
    frame_number = 0

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
arduino = Arduino(args.port)
state.time_start = state.time_processing_ended = datetime.now()
currentStage = -1
while True:
    frame_text = []
    state.frame_number = state.frame_number+1
    # grab the current frame
    (grabbed, frame) = camera.read()
    state.time_captured = datetime.now()
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if not grabbed:
        break

    # Detection works better on a blurred frame
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    mask = fgbg.apply(blurred)
    # It takes 120 frames to train background subtraction
    if (state.frame_number < 121):
        continue
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=1)
    (_, contours, _) = cv2.findContours(mask.copy(),
                                        cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
    if not(state.flipper_a_trained):
        frame_text.append("Training A")
        print("\rTraining A                 ", end="")
        # Check if flipper was pressed to add contours
        delta = datetime.now() - state.time_press_a
        if (delta < timedelta(milliseconds=100) and not(state.flipper_countour_sent)):
            print("flipper_a.add_contours(contours)")
            state.flipper_countour_sent = True
            print("state.flipper_a_trained = flipper_a.train()")
        elif (delta > timedelta(milliseconds=args.cooldown)):
            arduino.shortPressA()
            state.time_press_a = datetime.now()
            state.flipper_countour_sent = False
            frame_text.append("Short press A")
            sleep(0.01)  # Sleep 10ms to allow circuitry to trigger properly
    elif not(state.flipper_b_trained):
        print("\rTraining B                 ", end="")
        frame_text.append("Training B")
    else:
        print("\rGame in progress                 ", end="")
        frame_text.append("Game")

    # Draw contours we find on the original frame, for debugging
    if (args.show or args.out):
        for c in contours:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 80:
                continue

            # compute the bounding box for the contour, draw it on the frame
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # print('%d, %d; size: %d' % (x+w/2, y+h/2, cv2.contourArea(c)))

    # Processing END timeframe
    frame_text.insert(0, "{:06d} {}".format(state.frame_number, getSecondsString(state.time_captured-state.time_start)))
    frame_text.insert(1, "Capture: {}s".format(getSecondsString(state.time_captured-state.time_processing_ended)))
    # This needs to be assigned after ^ capture time calculation, so we can use the same timer.
    state.time_processing_ended = datetime.now()
    frame_text.insert(2, "Processing: {}s".format(getSecondsString(state.time_processing_ended-state.time_captured)))
    if (args.show or args.out):
        for i, line in enumerate(frame_text):
            y = 21 + i*20
            cv2.putText(frame, line, (1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    # Show original on the screen
    if (args.show):
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
if (args.out):
    out.release()
cv2.destroyAllWindows()

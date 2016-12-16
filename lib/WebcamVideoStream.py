# import the necessary packages
from threading import Thread
import cv2
from datetime import datetime
import os
from time import sleep

class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        if (os.path.isfile(src)):
            # Video file
            self.stream = cv2.VideoCapture(src)
            self.wait_for_read = True
        else:
            # Webcam
            self.wait_for_read = False
            self.stream = cv2.VideoCapture(int(src))
            self.stream.set(3, 640)  # width
            self.stream.set(4, 480)  # height
            self.stream.set(5, 60.0)  # fps
        (self.grabbed, self.frame) = self.stream.read()
        self.timestamp = datetime.now()
        self.frame_number = 1
        self.frame_read = False

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            print("Waiting for frame to be read")
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # If we need to wait for read, and it was not read yet, keep looping, with a 1ms sleep
            if self.wait_for_read and not(self.frame_read):
                sleep(0.001)
                print("Waiting for frame to be read")
                continue
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            self.timestamp = datetime.now()
            self.frame_number = self.frame_number + 1
            self.frame_read = False
            if not(self.grabbed):
                self.stopped = True

    def read(self):
        # Mark that we read the frame, so we can grab the next one from the file. Not used for actual camera
        self.frame_read = True
        # return the frame most recently read
        return {
            'stopped': self.stopped,
            'frame': self.frame,
            'number': self.frame_number,
            'timestamp': self.timestamp
            }

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def getParam(self, param):
        return self.stream.get(param)

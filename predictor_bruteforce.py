import cv2
from datetime import datetime
import math


class Bruteforce(object):

    # min_area: minimum contour area to be considered a plausible ball
    # max_area: maximum -----------||----------------
    # max_speed: maximum speed (pixels per millisecond) to be considered plausible travel
    def __init__(self, min_area, max_area, max_speed):
        self.min_area = min_area
        self.max_area = max_area
        self.max_speed = max_speed
        print("Setup things: %d %d %.06f" % (min_area, max_area, max_speed))
        self.contour_sets = []

    def add_contours(self, contours, time):
        self.contour_sets.insert(0, {"time": time, "contours": contours})
        if (len(self.contour_sets) > 2):
            # Remove oldest element and discard it, as we're only tracking 2 latest sets
            self.contour_sets.pop()

    # future defines how many milliseconds in the future we want to find the object
    def get_lines(self, future=60):
        if (len(self.contour_sets) < 2):
            return iter(())
        # time difference between lines
        delta = (self.contour_sets[0]["time"] - self.contour_sets[1]["time"]).microseconds
        lines = []
        for i in self.contour_sets[0]['contours']:
            if (cv2.contourArea(i) < self.min_area or cv2.contourArea(i) > self.max_area):
                continue
            i_coords = self.get_center_of_mass(i)
            for j in self.contour_sets[1]['contours']:
                if (cv2.contourArea(j) < self.min_area or cv2.contourArea(j) > self.max_area):
                    continue
                j_coords = self.get_center_of_mass(j)
                futureX = self.get_future(past=j_coords[0], present=i_coords[0], delta_micros=delta, future_ms=future)
                futureY = self.get_future(past=j_coords[1], present=i_coords[1], delta_micros=delta, future_ms=future)
                speed = self.get_speed(past=j_coords, present=i_coords, millis=delta/1000.0)
                if (speed>self.max_speed):
                    # print("Speed is too high: %.06f (limit: %.06f)" % (speed, self.max_speed))
                    continue
                lines.append({
                    'past': i_coords,
                    'present': j_coords,
                    'future': (futureX, futureY)
                })
        return lines

    def get_center_of_mass(self, contour):
        m = cv2.moments(contour)
        return (int(m['m10']/m['m00']), int(m['m01']/m['m00']))

    def get_speed(self, past, present, millis):
        distance = math.sqrt((present[0] - past[0]) ** 2 + (present[1] - past[1]) ** 2)
        return distance/millis

    def get_future(self, past, present, delta_micros, future_ms):
        speed = (present - past) / float(delta_micros)
        # future is in milliseconds, so need to multiply
        return int(present + (speed * future_ms * 1000))

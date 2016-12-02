import cv2
import collections

class Flipper(object):
    """Class to encapsulate all the flipper logic.

    Intended flow is:

        arduino = Arduino(...)
        left_flipper = Flipper(name='left')
        while(frame):
            contours = cv2.findContours(...)
            for c in contours:
                left_flipper.add_contour(contour)
            ...
        left_flipper.train()

        if not left_flipper.is_good():
            print "Uh-oh, I did not catch left flipper effective area."

        while(frame):
            balls = cv2.findContours(...)
            for c in balls:
                if left_flipper.check(ball):
                    machine.trigger_left()
    """

    def __init__(self, name=None):
        self.name = name
        self.effective_areas = []
        # make contours a circullar buffer, so it will not cause memory leaks
        self.contours = collections.deque(maxlen=50)

    def add_contour(self, contour):
        self.contours.append(contour)

    def train(self):
        areas = self.__analyze_contours()
        if len(areas) > 0:
            self.effective_areas.extend([Rectangle(a) for a in areas])
            return self.is_good()
        else:
            return False

    def is_good(self):
        return len(self.effective_areas) > 0

    def check(self, contour):
        "Checks that contour is in one of `self.effective_areas`"
        if self.is_good():
            target = Rectangle(cv2.boundingRect(contour))

            for area in self.effective_areas:
                if area.has_intersect(target):
                    return True

        return False

    def __analyze_contours(self):
        """Reads stored contours, analyze overlap, and produces effective
        contours
        """

        if len(self.contours) < 10:
            []

        approximations = map(cv2.boundingRect, self.contours)

        (overlaps, _) = cv2.groupRectangles(approximations, 6, 0.8)
        return overlaps


class Rectangle(object):
    def __init__(self, rect):
        self.rect = rect
        (self.x0, self.y0, self.w, self.h) = rect
        self.x1 = self.x0 + self.w
        self.y1 = self.y0 + self.h

    def has_intersect(self, rect):
        dx = min(self.x1, rect.x1) - max(self.x0, rect.x0)
        dy = min(self.y1, rect.y1) - max(self.y0, rect.y0)
        return (dx >= 0) and (dy >= 0)

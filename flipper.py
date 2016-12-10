import cv2
import collections
import numpy

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

    def __init__(self, name=None, num_masks=6, min_effective=3):
        self.name = name
        self.effective_areas = []
        self.masks = []  # Storing masks here
        self.num_masks = num_masks  # Number of masks to train on
        self.min_effective = min_effective  # Minimum number of occurrences we need to see to treat this as effective area
        # make contours a circullar buffer, so it will not cause memory leaks
        self.contours = collections.deque(maxlen=50)
        self.mask_contours = []
        self.hull_mask = None  # This will hold final trained areas hull contours filled.

    def add_contour(self, contour):
        self.contours.append(contour)

    def add_mask(self, mask):
        mask[mask > 0] = 1
        self.masks.insert(0, mask)
        if (len(self.masks) > self.num_masks):
            self.masks.pop()

    def train(self):
        areas = self.__analyze_contours()
        if len(areas) > 0:
            self.effective_areas.extend([Rectangle(a) for a in areas])
            return self.is_good()
        else:
            return False

    def train_masks(self):
        if (len(self.masks) < self.num_masks):
            return False
        # initialize mask with all zeroes
        self.combined_mask = numpy.zeros_like(self.masks[0])
        for m in self.masks:
            # All masks are 0 and 1, while allowing all the way up to 255
            self.combined_mask = self.combined_mask + m
        self.combined_mask[self.combined_mask >= self.min_effective] = 255
        self.combined_mask[self.combined_mask < 255] = 0
        return self.is_good_mask()

    def is_good(self):
        return len(self.effective_areas) > 0

    def is_good_mask(self):
        # minimum area that should be considered OK
        min_size = self.combined_mask.size/500
        (_, contours, _) = cv2.findContours(self.combined_mask.copy(),
                                            cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
        self.mask_contours = []
        self.hull_mask = numpy.zeros_like(self.combined_mask)
        for c in contours:
            if (cv2.contourArea(c) > min_size):
                self.mask_contours.append(cv2.convexHull(c))
        # If we didn't find any large enough contours, seems like our training is unsuccessful
        if len(self.mask_contours) > 0:
            # draw final convex hull contours, and fill them
            cv2.drawContours(self.hull_mask, self.mask_contours, -1, 255, -1)
            return True
        else:
            return False

    def get_trained_mask_contours(self):
        return self.mask_contours


    def check(self, contour):
        "Checks that contour is in one of `self.effective_areas`"
        if self.is_good():
            target = Rectangle(cv2.boundingRect(contour))

            for area in self.effective_areas:
                if area.has_intersect(target):
                    return True

        return False

    def check_line(self, p1, p2, line_thick=1):
        if self.hull_mask is None:
            return False

        line = numpy.zeros_like(self.hull_mask)
        cv2.line(line, p1, p2, 255, line_thick)
        if (numpy.count_nonzero(numpy.logical_and(line, self.hull_mask)) > 0):
            return True

        # By default, it's false
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
        # BEGIN: HACK
        # self.x0 = int(self.x0 - (self.w * 0.3))
        # self.y0 = int(self.y0 - (self.h))
        #
        # self.w = int(self.w * 1.3)
        # self.h = int(self.h * 1.5)
        # END: HACK
        self.x1 = self.x0 + self.w
        self.y1 = self.y0 + self.h


    def has_intersect(self, rect):
        # intersect if any of 4 points are inside the Rectangle
        if (rect.x0 > self.x0 and rect.x0 < self.x1 and
            rect.y0 > self.y0 and rect.y0 < self.y1):
            return True
        if (rect.x1 > self.x0 and rect.x1 < self.x1 and
            rect.y0 > self.y0 and rect.y0 < self.y1):
            return True
        if (rect.x0 > self.x0 and rect.x0 < self.x1 and
            rect.y1 > self.y0 and rect.y1 < self.y1):
            return True
        if (rect.x1 > self.x0 and rect.x1 < self.x1 and
           rect.y1 > self.y0 and rect.y1 < self.y1):
            return True
        return False
        dx = min(self.x1, rect.x1) - max(self.x0, rect.x0)
        dy = min(self.y1, rect.y1) - max(self.y0, rect.y0)
        return (dx >= 0) and (dy >= 0)

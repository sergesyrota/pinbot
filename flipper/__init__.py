import cv2


class Flipper(object):
    """Class to encapsulate all the flipper logic.

    Intended flow is:

        left_flipper = Flipper('left')
        while(frame):
            contours = cv2.findContours(...)
            left_flipper.add_contours(contours)
            ...
        left_flipper.train()

        if not left_flipper.is_good():
            print "Uh-oh, I did not catch left flipper effective area."

        while(frame):
            balls = cv2.findContours(...)
            if left_flipper.check(balls):
                machine.fire_flipper('left')
    """

    def __init__(self, name):
        self.name = name
        self.effective_areas = []
        self.contours = []

    def add_contour(self, contour):
        self.contours.append(contour)

    def train(self):
        areas = self.__analyze_contours()
        self.effective_areas.extend(areas)

        return self.is_good()

    def is_good(self):
        len(self.effective_areas) > 0

    def check(self, contour):
        """Checks that contour is in one of `self.effective_areas`
        """
        if self.is_good():
            # TODO
            pass
        False

    def __analyze_contours(self):
        """Reads stored contours, analyze overlap, and populate
        `self.effective_areas`.
        """
        # TODO
        pass

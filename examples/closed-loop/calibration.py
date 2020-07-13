import time

import cv2
import numpy as np


class Calibration_Extractor:
    def __init__(self, x=-1920, y=-50, w=1920, h=1080):
        self.x, self.y = x, y
        self.raw = np.zeros((h, w), dtype=float)

        self.mean = []
        self.fetch = lambda x: None

        self.settle_time = 10
        self.duration = 15

    def activate(self):
        self.start = time.time()
        self.fetch = self.r_fetch
        print("\nCalibration started.\nSettle time: {} seconds\nDuration: {} seconds".format(self.settle_time,
                                                                                             self.duration))

    def r_fetch(self, core):
        delta = time.time() - self.start
        if delta > self.settle_time:
            if len(self.mean) == 0:
                print("Calibration settled. Collecting data for {} seconds.".format(self.duration))
            if delta - self.settle_time > self.duration:
                print("\nCalibration finished.\nMean size: {}\nTerminating Puptrack..".format(
                    round(np.mean(self.mean), 2)))
                core.release()
                return

            w, h = core.dataout["pw"], core.dataout["ph"]

            if w == -1:
                core.dataout["calibration"] = -1
                return

            size = float(w * h)
            self.mean.append(size)

            core.dataout["calibration"] = [self.raw[0][0], np.mean(self.mean)]

        core.dataout["calibration"] = [self.raw[0][0], -1]
        cv2.imshow("Calibration", self.raw)
        cv2.moveWindow("Calibration", self.x, self.y)

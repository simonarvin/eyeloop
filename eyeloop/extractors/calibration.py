import time
from datetime import datetime
import cv2
import numpy as np

class Calibration_Extractor:
    def __init__(self, x=0, y=0, w=100, h=100):
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
                mean_value = round(np.mean(self.mean), 2)

                now = datetime.now()
                time_str = now.strftime("%Y%m%d%H%M%S")
                file_name = "{}._cal_".format(time_str)
                f = open(file_name, "w")
                f.write(str(mean_value))
                f.close()

                print("Calibration file saved as {}".format(file_name))

                print("\nCalibration finished.\nMean size: {}\nTerminating EyeLoop..".format(mean_value))

                core.release()
                return

            #((pupil_width, pupil_height), pupil_center, pupil_angle),
            w, h = core.dataout["pupil"][0]

            if w == -1:
                core.dataout["calibration"] = -1
                return

            size = float(w * h)
            self.mean.append(size)

            core.dataout["calibration"] = [self.raw[0][0], np.mean(self.mean)]

        core.dataout["calibration"] = [self.raw[0][0], -1]
        cv2.imshow("Calibration", self.raw)
        cv2.moveWindow("Calibration", self.x, self.y)

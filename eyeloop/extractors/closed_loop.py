import time

import cv2
import numpy as np


class ClosedLoop_Extractor:
    def __init__(self, MAXSIZE = 3231, x=-0, y=0, w=100, h=100):
        """
        RUN CALIBRATE, THEN SET MAXSIZE (= ._cal_ file value)
        """

        self.basesize = MAXSIZE / 2
        self.size = 0

        self.brightness = 0
        self.unit = np.ones((h, w), dtype=float)

        self.x, self.y = x, y

        self.velocity = 0
        self.index = 0

        self.q_coef = 0.1  # Scalar
        self.I_coef = .1  # Rate
        self.friction = .05

        self.state_dict = {
            1: "closed-loop",
            2: "white",
            0: "black"
        }

        self.protocol = [
            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.001,
                 "I_coef": 0.01,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.001,
                 "I_coef": 0.01,
                 "friction": 0.05
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.001,
                 "I_coef": 0.001,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.001,
                 "I_coef": 0.05,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.00025,
                 "I_coef": 0.01,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.0001,
                 "I_coef": 0.01,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.0005,
                 "I_coef": 0.2,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.0005,
                 "I_coef": 0.01,
                 "friction": 0.1
             }},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {
                 "q_coef": 0.0005,
                 "I_coef": 0.1,
                 "friction": 0.1
             }}
        ]

        self.total_steps = len(self.protocol)
        self.state = 0
        self.fetch = lambda x: None

        source = self.unit * self.brightness

    def activate(self):
        self.start = time.time()
        self.step_start = time.time()
        self.current = self.start

        self.fetch = self.r_fetch
        self.change_parameters(self.protocol[self.index])

    def timer(self):
        return time.time() - self.step_start

    def condition(self, step):
        cond = not (0 < self.current < step["t"])
        if cond:
            self.step_start = time.time()
        return cond

    def change_parameters(self, step):
        self.state = step["s"]

        print(
            "\nTransitioning to step {}/{}.\nstate changed to {}\nDuration: {}".format(self.index + 1, self.total_steps,
                                                                                       self.state_dict[self.state],
                                                                                       step["t"]).upper(), "seconds")
        for key, value in step["p"].items():
            print("     {} set to {}".format(key, value))
            exec("self." + key + '=' + str(value))

    def release(self):
        cv2.destroyAllWindows()

    def r_fetch(self, core):
        w, h = core.dataout["pupil"][0]
        size = float(w * h)

        if self.state == 2:
            # WHITE
            self.brightness = 1
        elif self.state == 0:
            # BLACK
            self.brightness = 0
        elif self.state == 1:
            # CLOSED LOOP

            if w != -1:
                self.velocity += (self.brightness - self.q_coef * size ** 2 / self.basesize) * self.I_coef
                self.velocity -= self.velocity * self.friction
                self.velocity = round(self.velocity, 3)

                self.brightness -= self.velocity

                self.brightness = min(self.brightness, 1)
                self.brightness = max(self.brightness, 0)

        step = self.protocol[self.index]

        self.current = self.timer()
        if self.condition(step):
            self.index += 1
            core.dataout["trigger"] = 1
            if self.index == len(self.protocol):
                print("Protocol finished. Terminating EyeLoop..")
                core.release()
                return
            else:
                self.change_parameters(self.protocol[self.index])
        else:
            core.dataout["trigger"] = 0

        # self.arr.append(self.brightness)
        core.dataout["closed_looptest"] = self.brightness
        core.dataout["closed_loopparam"] = step

        source = self.unit * self.brightness ** 2

        cv2.imshow("Brightness Test", source)
        cv2.moveWindow("Brightness Test", self.x, self.y)

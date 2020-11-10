import time

import cv2
import numpy as np


class Open_Loop_extractor():
    def __init__(self, x: int = 50, y: int = 50, w: int = 50, h: int = 50) -> None:

        self.fetch = lambda x: None

        self.raw = np.ones((h, w), dtype=float)
        self.frequency = .01
        self.phase = 0

        self.x, self.y = x, y

        self.state = 0

        self.state_dict = {
            1: "open-loop",
            2: "white",
            0: "black"
        }

        self.index = 0

        self.protocol = [
            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.1}},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.2}},

            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.4}},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.8}},

            {"t": 6,
             "s": 0,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.01}},

            {"t": 6,
             "s": 2,
             "p": {}},

            {"t": 60,
             "s": 1,
             "p": {"frequency": 0.05}},

            {"t": 6,
             "s": 2,
             "p": {}}
        ]

        self.total_steps = len(self.protocol)

    def activate(self) -> None:
        self.start = time.time()
        self.step_start = time.time()
        self.current = self.start

        self.fetch = self.r_fetch
        self.change_parameters(self.protocol[self.index])

    def timer(self, time) -> float:
        return time - self.step_start

    def condition(self, step, time) -> bool:
        cond = not (0 < self.current < step["t"])
        if cond:
            self.step_start = time #time.time()
        return cond

    def release(self):
        return

    def change_parameters(self, step) -> None:
        self.state = step["s"]

        print(
            "\nTransitioning to step {}/{}.\nstate changed to {}\nDuration: {}".format(self.index + 1, self.total_steps,
                                                                                       self.state_dict[self.state],
                                                                                       step["t"]).upper(), "seconds")
        for key, value in step["p"].items():
            print("     {} set to {}".format(key, value))
            exec("self." + key + '=' + str(value))

    def r_fetch(self, engine):
        if self.state == 2:
            # WHITE
            source = self.raw * 255
            self.phase = 0

        elif self.state == 0:
            # BLACK
            source = self.raw * 0
            self.phase = 0

        elif self.state == 1:
            # OPEN LOOP
            source = self.raw * np.sin(self.phase) * .5 + .5
            self.phase += self.frequency

        step = self.protocol[self.index]
        engine.dataout["open_looptest"] = source[0][0]
        engine.dataout["open_loopparam"] = step

        self.current = self.timer(engine.dataout["time"])

        if self.condition(step,engine.dataout["time"]):
            self.index += 1
            engine.dataout["trigger"] = 1
            if self.index == len(self.protocol):
                print("Protocol finished. Terminating Puptrack..")
                engine.release()
                return
            else:
                self.change_parameters(self.protocol[self.index])
        else:
            engine.dataout["trigger"] = 0

        cv2.imshow("Open-loop", source)
        cv2.moveWindow("Open-loop", self.x, self.y)

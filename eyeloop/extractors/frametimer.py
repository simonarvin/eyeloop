import time


class FPS_extractor:
    """
    Simple fps-counter. Acts as an interface. Pass it to CORE(interfaces=[..]) in puptrack.py.
    """

    def __init__(self, max_iter=100):
        self.max_iter = max_iter
        self.reset()

    def activate(self):
        return

    def reset(self):
        self.iteration = 0
        self.start = time.time()

    def fetch(self, core):
        self.iteration += 1
        if self.iteration == self.max_iter:
            framerate = self.max_iter / (time.time() - self.start)

            print("    Currently processing {} frames per second.".format(int(framerate)))
            self.reset()

    def release(self):
        return

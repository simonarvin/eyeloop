import time
import threading
import eyeloop.config as config

class FPS_extractor:
    """
    Simple fps-counter. Acts as an interface. Pass it to CORE(interfaces=[..]) in puptrack.py.
    """

    def __init__(self):
        self.fetch = lambda _: None
        self.activate = lambda: None

        self.last_frame = 0

        self.thread = threading.Timer(1, self.get_fps)
        self.thread.start()


    def get_fps(self):
        print(f"    Processing {config.importer.frame - self.last_frame} frames per second.")
        self.last_frame = config.importer.frame
        self.thread = threading.Timer(1, self.get_fps)
        self.thread.start()


    def release(self, core):
        self.thread.cancel()

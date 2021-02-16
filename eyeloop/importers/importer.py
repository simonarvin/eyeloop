import cv2
import numpy as np

import eyeloop.config as config
from eyeloop.utilities.general_operations import tuple_int


class IMPORTER:

    def __init__(self):
        self.live = True
        self.scale = config.arguments.scale

        self.frame = 0
        self.vid_path = config.arguments.video
        self.capture = None

        if config.arguments.save == 1:
            self.save_ = self.save
        else:
            self.save_ = lambda _: None

        if config.arguments.rotation == 1:
            self.rotate_ = self.rotate
        else:
            self.rotate_ = lambda img, _: None

    def arm(self, width, height, image):

        self.dimensions = tuple_int((width * self.scale, height * self.scale))

        width, height = self.dimensions

        self.center = (width // 2, height // 2)

        if self.scale == 1:
            self.resize = lambda img: img
        else:
            self.resize = self.resize_image

        self.resize(image)

        # image = self.rotate(image, self.ENGINE.angle)
        
        config.engine.arm(width, height, image)

    def rotate(self, image: np.ndarray, angle: int) -> np.ndarray:
        """
        Performs rotaiton of the image to align visual axes.
        """

        if angle == 0:
            return

        M = cv2.getRotationMatrix2D(self.center, angle, 1)

        image[:] = cv2.warpAffine(image, M, self.dimensions, cv2.INTER_NEAREST)

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resizes image to scale value. -sc 1 (default)
        """

        return cv2.resize(image, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST)

    def save(self, image: np.ndarray) -> None:
        config.file_manager.save_image(image, self.frame)

    def release(self):
        self.release = lambda:None
        config.engine.release()

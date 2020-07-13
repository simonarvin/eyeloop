import cv2
import numpy as np

import config
from utilities.general_operations import tuple_int


class IMPORTER:

    def __init__(self):
        self.live = True
        self.scale = config.arguments.scale
        self.frame = 0
        self.vid_path = config.arguments.video

    def arm(self, width, height, image):
        self.frame = 0
        self.vid_path = config.engine.arguments.video

    def arm(self, width, height, image):

        self.dimensions = tuple_int((width * self.scale, height * self.scale))

        width, height = self.dimensions

        self.center = (width // 2, height // 2)

        if self.scale == 1:
            self.resize = lambda x: x
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
            return image

        M = cv2.getRotationMatrix2D(self.center, angle, 1)

        return cv2.warpAffine(image, M, self.dimensions)

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resizes image to scale value. -sc 1 (default)
        """

        return cv2.resize(image, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST)

    def save(self, image: np.ndarray) -> None:
        config.file_manager.save_image(image, self.frame)

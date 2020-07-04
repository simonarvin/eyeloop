import numpy as np
import cv2
from utilities.general_operations import tuple_int

class IMPORTER:
    def arm(self, width, height, image):
        self.frame          =   0
        self.dimensions = tuple_int((width * self.scale, height * self.scale))

        width, height = self.dimensions

        self.center = (width // 2, height // 2)

        self.resize(image)

        #image = self.rotate(image, self.ENGINE.angle)
        self.ENGINE.importer = self
        self.ENGINE.arm(width, height, image)

    def rotate(self, image:np.ndarray, angle:int) -> np.ndarray:
        """
        Performs rotaiton of the image to align visual axes.
        """

        if angle == 0:
            return image

        M = cv2.getRotationMatrix2D(self.center, angle, 1)

        return cv2.warpAffine(image, M, self.dimensions)

    def resize_image(self, image:np.ndarray) -> np.ndarray:
        """
        Resizes image to scale value. -sc 1 (default)
        """

        return cv2.resize(image, None, fx = self.scale, fy = self.scale, interpolation = cv2.INTER_NEAREST)

    def save(self, image:np.ndarray) -> None:
        self.file_manager.save_image(image, self.frame)

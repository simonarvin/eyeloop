import time
import os
import cv2
import numpy as np

class File_Manager:
    """
    The file manager...
    - Generates a unique, time-stamped folder
    which extractors may access via file_manager.new_folderpath.
    - Reads image sequences for offline analysis.
    - Saves images from camera streams.
    """
    def __init__(self, dir:str) -> None:

        self.directory = dir + "/data"

        try:
            os.mkdir(self.directory)
        except FileExistsError:
            print("'{}' already exists.".format(self.directory))

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.new_folderpath = "{}/trial_{}".format(self.directory, timestamp)

        os.mkdir(self.new_folderpath)

    def save_image(self, image:np.ndarray, frame:int) -> None:
        """
        Saves video sequence to new folderpath.
        """

        file = r'{}/frame_{}.jpg'.format(self.new_folderpath, frame)
        cv2.imwrite(file, image)

    def read_image(self, frame:int) -> np.ndarray:
        """
        Reads video sequence from the input folderpath.
        Command-line argument -v [dir] sets this path.
        """

        return np.array(cv2.imread("{}/frame_{}.jpg".format(self.input_folderpath, frame)))

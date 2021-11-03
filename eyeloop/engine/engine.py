import logging
import time
from typing import Optional

import cv2

import eyeloop.config as config
from eyeloop.constants.engine_constants import *
from eyeloop.engine.processor import Shape
from eyeloop.utilities.general_operations import to_int, tuple_int

logger = logging.getLogger(__name__)


class Engine:
    def __init__(self, eyeloop):

        self.live = True  # Access this to check if Core is running.

        self.eyeloop = eyeloop
        self.model = config.arguments.model  # Used for assigning appropriate circular model.
        self.extractors = []
        self.blink_threshold = config.arguments.bthreshold

        if config.arguments.tracking == 0:  # Recording mode. --tracking 0
            self.iterate = self.record
        else:  # Tracking mode. --tracking 1 (default)
            self.iterate = self.track

        self.angle = 0

        self.cr_processor_1 = Shape(type = 2, n = 1)
        self.cr_processor_2 = Shape(type = 2, n = 2)
        self.pupil_processor = Shape()

        #   Via "gui", assign "refresh_pupil" to function "processor.refresh_source"
        #   when the pupil has been selected.
        self.refresh_pupil = lambda x: None

    def load_extractors(self, extractors: list = None) -> None:
        if extractors is None:
            extractors = []
        logger.info(f"loading extractors: {extractors}")
        self.extractors = extractors


    def run_extractors(self) -> None:
        """
        Calls all extractors at the end of each time-step.
        Assign additional extractors to core engine via eyeloop.py.
        """

        for extractor in self.extractors:
            try:
                extractor.fetch(self)
            except Exception as e:
                print("Error in module class: {}".format(extractor.__name__))
                print("Error message: ", e)

    def record(self) -> None:
        """
        Runs Core engine in record mode. Timestamps all frames in data output log.
        Runs gui update_record function with no tracking.
        Argument -s 1
        """

        timestamp = time.time()

        self.dataout = {
            "time": timestamp
        }

        config.graphical_user_interface.update_record(self.source)

        self.run_extractors()

    def arm(self, width, height, image) -> None:

        self.width, self.height = width, height
        config.graphical_user_interface.arm(width, height)
        self.center = (width//2, height//2)

        self.iterate(image)

        self.pupil_processor.binarythreshold = float(np.min(image)) * .7 + 50
        self.cr_processor_1.binarythreshold = self.cr_processor_2.binarythreshold = float(np.min(image)) * .7 + 150


    def track(self, img) -> None:
        """
        Executes the tracking algorithm on the pupil and corneal reflections.
        First, blinking is analyzed.
        Second, corneal reflections are detected.
        Third, corneal reflections are inverted at pupillary overlap.
        Fourth, pupil is detected.
        Finally, data is logged and extractors are run.
        """
        mean_img = np.mean(img)
        try:

            config.blink[config.blink_i] = mean_img
            config.blink_i += 1

        except IndexError:
            config.blink_i = 0

        self.dataout = {
            "time": time.time()
        }


        if mean_img < np.mean(config.blink):
            self.dataout["blink"] = 1

        else:

            self.pupil_processor.track(img)

            self.cr_processor_1.track(img)
        #self.cr_processor_2.track(img.copy(), img)


        try:
            config.graphical_user_interface.update(img)
        except Exception as e:
            logger.exception("Did you assign the graphical user interface (GUI) correctly? Attempting to release()")
            self.release()
            return

        self.run_extractors()

    def activate(self) -> None:
        """
        Ativates all extractors.
        The extractor activate() function is optional.
        """

        for extractor in self.extractors:
            try:
                extractor.activate()
            except AttributeError:
                logger.warning(f"Extractor {extractor} has no activate() method")

    def release(self) -> None:
        """
        Releases/deactivates all running process, i.e., importers, extractors.
        """

        self.live = False
        config.graphical_user_interface.release()

        for extractor in self.extractors:
            try:
                extractor.release(self)
            except AttributeError:
                logger.warning(f"Extractor {extractor} has no release() method")
            else:
                pass

        config.importer.release()

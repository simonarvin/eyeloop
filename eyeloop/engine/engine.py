import logging
import time
from typing import Optional
from os.path import dirname, abspath
import glob, os

import cv2

import eyeloop.config as config
from eyeloop.constants.engine_constants import *
from eyeloop.engine.processor import Shape
from eyeloop.utilities.general_operations import to_int, tuple_int

logger = logging.getLogger(__name__)
PARAMS_DIR = f"{dirname(dirname(abspath(__file__)))}/engine/params"

class Engine:
    def __init__(self, eyeloop):

        self.live = True  # Access this to check if Core is running.

        self.eyeloop = eyeloop
        self.model = config.arguments.model  # Used for assigning appropriate circular model.

        self.extractors = []

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

        if config.arguments.blinkcalibration != "":
            config.blink = np.load(config.arguments.blinkcalibration)
            self.blink_sampled = lambda _:None
            logger.info("(success) blink calibration loaded")

        if config.arguments.clear == False or config.arguments.params != "":

            try:
                if config.arguments.params != "":
                    latest_params = max(glob.glob(config.arguments.params), key=os.path.getctime)

                    print(config.arguments.params + " loaded")

                else:
                    latest_params = max(glob.glob(PARAMS_DIR + "/*.npy"), key=os.path.getctime)

                params_ = np.load(latest_params, allow_pickle=True).tolist()

                self.pupil_processor.binarythreshold, self.pupil_processor.blur = params_["pupil"][0], params_["pupil"][1]

                self.cr_processor_1.binarythreshold, self.cr_processor_1.blur = params_["cr1"][0], params_["cr1"][1]
                self.cr_processor_2.binarythreshold, self.cr_processor_2.blur = params_["cr2"][0], params_["cr2"][1]

                print("(!) Parameters reloaded. Run --clear 1 to prevent this.")


                param_dict = {
                "pupil" : [self.pupil_processor.binarythreshold, self.pupil_processor.blur],
                "cr1" : [self.cr_processor_1.binarythreshold, self.cr_processor_1.blur],
                "cr2" : [self.cr_processor_2.binarythreshold, self.cr_processor_2.blur]
                }

                logger.info(f"loaded parameters:\n{param_dict}")

                return

            except:
                pass


        filtered_image = image[np.logical_and((image < 220), (image > 30))]
        self.pupil_processor.binarythreshold = np.min(filtered_image) * 1 + np.median(filtered_image) * .1#+ 50
        self.cr_processor_1.binarythreshold = self.cr_processor_2.binarythreshold = float(np.min(filtered_image)) * .7 + 150

        param_dict = {
        "pupil" : [self.pupil_processor.binarythreshold, self.pupil_processor.blur],
        "cr1" : [self.cr_processor_1.binarythreshold, self.cr_processor_1.blur],
        "cr2" : [self.cr_processor_2.binarythreshold, self.cr_processor_2.blur]
        }

        logger.info(f"loaded parameters:\n{param_dict}")


    def blink_sampled(self, t:int = 1):

        if t == 1:
            if config.blink_i% 20 == 0:
                print(f"calibrating blink detector {round(config.blink_i/config.blink.shape[0]*100,1)}%")
        else:
            logger.info("(success) blink detection calibrated")
            path = f"{config.file_manager.new_folderpath}/blinkcalibration_{self.dataout['time']}.npy"
            np.save(path, config.blink)
            print("blink calibration file saved")

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
            self.blink_sampled(1)

        except IndexError:
            self.blink_sampled(0)
            self.blink_sampled = lambda _:None
            config.blink_i = 0

        self.dataout = {
            "time": time.time()
        }

        if np.abs(mean_img - np.mean(config.blink[np.nonzero(config.blink)])) > 10:

            self.dataout["blink"] = 1
            self.pupil_processor.fit_model.params = None
            logger.info("Blink detected.")
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
        Activates all extractors.
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
        try:
            config.graphical_user_interface.out.release()
        except:
            pass

        param_dict = {
        "pupil" : [self.pupil_processor.binarythreshold, self.pupil_processor.blur],
        "cr1" : [self.cr_processor_1.binarythreshold, self.cr_processor_1.blur],
        "cr2" : [self.cr_processor_2.binarythreshold, self.cr_processor_2.blur]
        }

        path = f"{config.file_manager.new_folderpath}/params_{self.dataout['time']}.npy"
        np.save(path, param_dict)
        print("Parameters saved")

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

import logging
from pathlib import Path
from typing import Optional, Callable

import cv2

import eyeloop.config as config
from eyeloop.importers.importer import IMPORTER

logger = logging.getLogger(__name__)


class Importer(IMPORTER):

    def __init__(self) -> None:
        super().__init__()
        self.route_frame: Optional[Callable] = None  # Dynamically assigned at runtime depending on input type

    def first_frame(self) -> None:
        self.vid_path = Path(config.arguments.video)
        # load first frame
        if str(self.vid_path.name) == "0" or self.vid_path.is_file():  # or stream
            if str(self.vid_path.name) == "0":
                self.capture = cv2.VideoCapture(0)
            else:
                self.capture = cv2.VideoCapture(str(self.vid_path))

            self.route_frame = self.route_cam
            width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            _, image = self.capture.read()
            if self.capture.isOpened():
                try:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                except:
                    image = image[..., 0]
            else:
                raise ValueError(
                    "Failed to initialize video stream.\n"
                    "Make sure that the video path is correct, or that your webcam is plugged in and compatible with opencv.")

        elif self.vid_path.is_dir():

            config.file_manager.input_folderpath = self.vid_path

            config.file_manager.input_folderpath = self.vid_path

            image = config.file_manager.read_image(self.frame)

            try:
                height, width, _ = image.shape
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.route_frame = self.route_sequence_sing
            except Exception:  # TODO fix bare except
                logger.exception("first_frame() error: ")
                height, width = image.shape
                self.route_frame = self.route_sequence_flat

        else:
            raise ValueError(f"Video path at {self.vid_path} is not a file or directory!")

        self.arm(width, height, image)

    def route(self) -> None:
        self.first_frame()
        while True:
            if self.route_frame is not None:
                self.route_frame()
            else:
                break

    def proceed(self, image) -> None:
        image = self.resize(image)
        image = self.rotate(image, config.engine.angle)
        config.engine.update_feed(image)
        self.save(image)
        self.frame += 1

    def route_sequence_sing(self) -> None:

        image = config.file_manager.read_image(self.frame)

        self.proceed(image[..., 0])

    def route_sequence_flat(self) -> None:

        image = config.file_manager.read_image(self.frame)

        self.proceed(image)

    def route_cam(self) -> None:
        """
        Routes the capture frame to:
        1: eyeloop for online processing
        2: frame save for offline processing
        """

        _, image = self.capture.read()
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.proceed(image)
        else:
            logger.info("No more frames to process, exiting.")
            self.release()

    def release(self) -> None:
        logger.debug(f"cv.Importer.release() called")
        if self.capture is not None:
            self.capture.release()

        self.route_frame = None
        cv2.destroyAllWindows()

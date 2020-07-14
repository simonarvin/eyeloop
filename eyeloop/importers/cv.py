from pathlib import Path

import cv2

import config
from importers.importer import IMPORTER


class Importer(IMPORTER):

    def __init__(self) -> None:
        super().__init__()

    def first_frame(self) -> None:
        self.vid_path = Path(config.arguments.video)
        # load first frame
        if self.vid_path.name == "0" or self.vid_path.is_file():  # or stream
            if self.vid_path.name == "0":
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
                raise ValueError("Failed to initialize video stream.\nMake sure that the video path is correct, or that your webcam is plugged in and compatible with opencv.")

        elif self.vid_path.is_dir():

            config.file_manager.input_folderpath = self.vid_path

            config.file_manager.input_folderpath = self.vid_path

            image = config.file_manager.read_image(self.frame)

            try:
                height, width, _ = image.shape
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.route_frame = self.route_sequence_sing
            except:  # TODO fix bare except
                height, width = image.shape
                self.route_frame = self.route_sequence_flat

        else:
            raise ValueError(f"Video path at {self.vid_path} is not a file or directory!")

        self.arm(width, height, image)

    def route(self) -> None:
        self.first_frame()
        try:
            while True:
                self.route_frame()
        except Exception as e:
            print(e)
            print("Importer released.")

    def proceed(self, image) -> None:
        image = self.resize(image)
        image = self.rotate(image, config.engine.angle)
        config.engine.update_feed(image)
        self.save(image)
        self.frame += 1

    def route_sequence_sing(self) -> None:

        image = config.file_manager.read_image(self.frame)[..., 0]
        self.proceed(image)

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

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        self.proceed(image)

    def release(self) -> None:
        self.route_frame = lambda _: None

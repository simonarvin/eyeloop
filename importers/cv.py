import cv2
from utilities.general_operations import check_path_type
from importers.importer import IMPORTER

class Importer(IMPORTER):
    def __init__(self, ENGINE) -> None:

        arguments = ENGINE.arguments
        self.ENGINE = ENGINE
        self.path = video = arguments.video
        pathtype = check_path_type(self.path)

        self.scale = arguments.scale

        if self.scale == 1:
            self.resize = lambda x: x
        else:
            self.resize = self.resize_image

        self.file_manager = ENGINE.file_manager

        if pathtype == "file": #or stream
            self.capture        =   cv2.VideoCapture(video)
            self.route_frame = self.route_cam
            width          =   self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height         =   self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            _, image    =   self.capture.read()
            image=image[...,0]

        elif pathtype == "folder":


            self.file_manager.input_folderpath = self.path

            image = self.file_manager.read_image(self.frame)
            try:
                height, width, _ = image.shape
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.route_frame = self.route_sequence_sing
            except:
                height, width = image.shape
                self.route_frame = self.route_sequence_flat

        self.arm(width, height, image)


    def route(self) -> None:
        try:
            while True:
                self.route_frame()
        except:
            print("Importer released.")


    def route_sequence_sing(self) -> None:

        image = self.file_manager.read_image(self.frame)[...,0]

        image = self.resize(image)
        image = self.rotate(image, self.ENGINE.angle)
        self.ENGINE.update_feed(image)
        self.save(image)
        self.frame += 1

    def route_sequence_flat(self) -> None:

        image = self.file_manager.read_image(self.frame)

        image=self.rotate(image, self.ENGINE.angle)

        image=self.resize(image)

        self.ENGINE.update_feed(image)
        self.save(image)
        self.frame += 1


    def route_cam(self) -> None:
        """
        Routes the capture frame to:
        1: puptrack for online processing
        2: frame save for offline processing
        """

        _, image    =   self.capture.read()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image = self.rotate(image, self.ENGINE.angle)
        image = self.resize(image)

        self.ENGINE.update_feed(image)
        self.save(image)
        self.frame+=1


    def release(self) -> None:
        self.route_frame = lambda _: None

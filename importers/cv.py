import cv2
from utilities.general_operations import check_path_type
from importers.importer import IMPORTER
import config

class Importer(IMPORTER):

    def __init__(self) -> None:
        super().__init__()



    def first_frame(self)->None:
        self.path = config.arguments.video
        pathtype = check_path_type(self.path)

        # load first frame
        if pathtype == "file": #or stream
            if self.path == "0":
                self.capture        =   cv2.VideoCapture(0)
            else:
                self.capture        =   cv2.VideoCapture(self.path)

            self.route_frame = self.route_cam
            width          =   self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height         =   self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            _, image    =   self.capture.read()
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            except:
                image=image[...,0]
        elif pathtype == "folder":


            self.file_manager.input_folderpath = self.path

            config.file_manager.input_folderpath = self.path

            image = config.file_manager.read_image(self.frame)


            try:
                height, width, _ = image.shape
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.route_frame = self.route_sequence_sing
            except:
                height, width = image.shape
                self.route_frame = self.route_sequence_flat


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

        image = config.file_manager.read_image(self.frame)[...,0]
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

        _, image    =   self.capture.read()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        self.proceed(image)


    def release(self) -> None:
        self.route_frame = lambda _: None

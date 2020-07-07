import time
from pymba import Vimba
from pymba import Frame
from importers.importer import IMPORTER
import config

#For pymba documentation, see:
#https://github.com/morefigs/pymba

class Importer(IMPORTER):


    def start(self)->None:
        # load first frame
        with Vimba() as vimba:
            camera = vimba.camera(0)
            camera.open()
            camera.arm('SingleFrame')
            frame = camera.acquire_frame()
            camera.disarm()

        image = frame.buffer_data_numpy()
        height, width = frame.shape

        self.arm(width, height, image)

    def acquire_frame(self, frame: Frame, delay: int = 1) -> None:
        """
        Routes the capture frame to two destinations:
        1: EyeLoop for online processing
        2: frame save for offline processing

        :param frame: The frame object to display.
        :param delay: Display delay in milliseconds, use 0 for indefinite.
        """


        image = frame.buffer_data_numpy()

        #image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)

        image = self.rotate(image, config.engine.angle)

        image = self.resize(image)
        config.engine.update_feed(image)
        self.save(image)

        self.frame += 1

    def release(self) -> None:
        self.live = False

    def route(self) -> None:
        with Vimba() as vimba:

            camera = vimba.camera(0)

            camera.open()

            camera.ExposureTime = 200 # play around with this if exposure is too low
            camera.ExposureAuto = "Off"
            camera.AcquisitionFrameRateMode = 'Basic'

            max_fps = camera.AcquisitionFrameRate
            camera.AcquisitionFrameRate = max_fps

            # arm the camera and provide a function to be called upon frame ready
            camera.arm('Continuous', self.acquire_frame)
            camera.start_frame_acquisition()

            while self.live:
                time.sleep(0.1)

            print("Terminating capture...")

            camera.stop_frame_acquisition()
            camera.disarm()

            camera.close()

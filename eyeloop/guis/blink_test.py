import cv2
import eyeloop.config as config
import numpy as np
from os.path import dirname, abspath

class GUI:
    def __init__(self) -> None:
        self.frames = []

        self.last_frame = 500
        self.pick = np.arange(10, self.last_frame, 50)
        self.filter = np.zeros(len(self.pick))

    def arm(self, width: int, height: int) -> None:
        return

    def update(self, img):
        if config.importer.frame == self.last_frame:

            stack = np.hstack(tuple(self.frames))
            cv2.imshow("Blink_test", stack)


            key = cv2.waitKey(1)
            _input = input("type the non-blinking frames, split by comma (0 from the left)")
            frames = np.array(_input.split(","),dtype=int)
            frames_ = np.array(self.frames)
            #print(frames)
            path = dirname(dirname(abspath(__file__)))+"/blink_.npy"

            data = [np.mean(frames_[frames])]

            np.save(path, data)
            print(f"data saved: {data}")

            config.engine.release()
        else:
            if config.importer.frame in self.pick:
                self.frames.append(img)

        #    cv2.imshow("Blink_test", img)
        #    key = cv2.waitKey(1)
            #if key == ord("q"):
            #    config.engine.release()
                #self.release()


    def release(self):
        #self.out.release()
        cv2.destroyAllWindows()

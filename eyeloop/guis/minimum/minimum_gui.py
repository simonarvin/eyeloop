import os
from pathlib import Path

import numpy as np

import eyeloop.config as config
from eyeloop.constants.minimum_gui_constants import *
from eyeloop.utilities.general_operations import to_int, tuple_int
import threading

import logging
logger = logging.getLogger(__name__)

class GUI:
    def __init__(self) -> None:


        dir_path = os.path.dirname(os.path.realpath(__file__))
        tool_tip_dict = ["tip_1_cr", "tip_2_cr", "tip_3_pupil", "tip_4_pupil", "tip_5_start", "tip_1_cr_error", "",
                         "tip_3_pupil_error"]
        self.first_tool_tip = cv2.imread("{}/graphics/{}.png".format(dir_path, "tip_1_cr_first"), 0)
        self.tool_tips = [cv2.imread("{}/graphics/{}.png".format(dir_path, tip), 0) for tip in tool_tip_dict]

        self._state = "adjustment"
        self.inquiry = "none"
        self.terminate = -1
        self.update = self.adj_update#real_update
        self.skip = 0
        self.first_run = True

        self.pupil_ = lambda _: False
        self.cr1_ = lambda _: False
        self.cr2_ = lambda _: False





    def tip_mousecallback(self, event, x: int, y: int, flags, params) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            if 10 < y < 35:
                if 20 < x < 209:
                    x -= 27
                    x = int(x / 36) + 1

                    self.update_tool_tip(x)

    def mousecallback(self, event, x, y, flags, params) -> None:
        x = x % self.width
        self.cursor = (x, y)

    def release(self):
        #self.out.release()
        cv2.destroyAllWindows()

    def remove_mousecallback(self) -> None:
        cv2.setMouseCallback("CONFIGURATION", lambda *args: None)
        cv2.setMouseCallback("Tool tip", lambda *args: None)

    def update_tool_tip(self, index: int, error: bool = False) -> None:
        if error:
            cv2.imshow("Tool tip", self.tool_tips[index + 4])
        else:
            cv2.imshow("Tool tip", self.tool_tips[index - 1])

    def key_listener(self, key: int) -> None:
        try:
            key = chr(key)
        except:
            return

        if self.inquiry == "track":
            if "y" == key:
                print("Initiating tracking..")
                self.remove_mousecallback()
                cv2.destroyWindow("CONFIGURATION")
                cv2.destroyWindow("BINARY")
                cv2.destroyWindow("Tool tip")

                cv2.imshow("TRACKING", self.bin_stock)
                cv2.moveWindow("TRACKING", 100, 100)

                self._state = "tracking"
                self.inquiry = "none"

                self.update = self.real_update

                config.engine.activate()

                return
            elif "n" == key:
                print("Adjustments resumed.")
                self._state = "adjustment"
                self.inquiry = "none"
                return

        if self._state == "adjustment":
            if key == "p":
                config.engine.angle -= 3

            elif key == "o":
                config.engine.angle += 3

            elif "1" == key:
                try:
                    #config.engine.pupil = self.cursor
                    self.pupil_processor.reset(self.cursor)
                    self.pupil_ = self.pupil

                    self.update_tool_tip(4)

                    print("Pupil selected.\nAdjust binarization via R/F (threshold) and T/G (smoothing).")
                except Exception as e:
                    self.update_tool_tip(3, True)
                    logger.info(f"pupil selection failed; {e}")

            elif "2" == key:
                try:

                    self.cr_processor_1.reset(self.cursor)
                    self.cr1_ = self.cr_1

                    self.current_cr_processor = self.cr_processor_1

                    self.update_tool_tip(2)

                    print("Corneal reflex selected.\nAdjust binarization via W/S (threshold) and E/D (smoothing).")

                except Exception as e:
                    self.update_tool_tip(1, True)
                    logger.info(f"CR selection failed; {e}")

            elif "3" == key:
                try:
                    self.update_tool_tip(2)
                    self.cr_processor_2.reset(self.cursor)
                    self.cr2_ = self.cr_2

                    self.current_cr_processor = self.cr_processor_2

                    print("\nCorneal reflex selected.")
                    print("Adjust binarization via W/S (threshold) and E/D (smoothing).")

                except:
                    self.update_tool_tip(1, True)
                    print("Hover and click on the corneal reflex, then press 3.")


            elif "z" == key:
                print("Start tracking? (y/n)")
                self.inquiry = "track"

            elif "w" == key:

                self.current_cr_processor.binarythreshold += 1

                # print("Corneal reflex binarization threshold increased (%s)." % self.CRProcessor.binarythreshold)

            elif "s" == key:

                self.current_cr_processor.binarythreshold -= 1
                # print("Corneal reflex binarization threshold decreased (%s)." % self.CRProcessor.binarythreshold)

            elif "e" == key:

                self.current_cr_processor.blur = tuple([x + 2 for x in self.current_cr_processor.blur])
                # print("Corneal reflex blurring increased (%s)." % self.CRProcessor.blur)

            elif "d" == key:

                if self.current_cr_processor.blur[0] > 1:
                    self.current_cr_processor.blur -= tuple([x - 2 for x in self.current_cr_processor.blur])
                # print("Corneal reflex blurring decreased (%s)." % self.CRProcessor.blur)

            elif "r" == key:

                self.pupil_processor.binarythreshold += 1
                # print("Pupil binarization threshold increased (%s)." % self.pupil_processor.binarythreshold)
            elif "f" == key:

                self.pupil_processor.binarythreshold -= 1
                # print("Pupil binarization threshold decreased (%s)." % self.pupil_processor.binarythreshold)

            elif "t" == key:

                self.pupil_processor.blur = tuple([x + 2 for x in self.pupil_processor.blur])

                # print("Pupil blurring increased (%s)." % self.pupil_processor.blur)

            elif "g" == key:
                if self.pupil_processor.blur[0] > 1:
                    self.pupil_processor.blur = tuple([x - 2 for x in self.pupil_processor.blur])
                # print("Pupil blurring decreased (%s)." % self.pupil_processor.blur)

        if "q" == key:
            # Terminate tracking
            config.engine.release()

    def arm(self, width: int, height: int) -> None:
        self.fps = np.round(1/config.arguments.fps, 2)

        self.pupil_processor = config.engine.pupil_processor

        self.cr_index = 0
        self.current_cr_processor = config.engine.cr_processor_1  # primary corneal reflection
        self.cr_processor_1 = config.engine.cr_processor_1
        self.cr_processor_2 = config.engine.cr_processor_2

        self.width, self.height = width, height
        self.binary_width = max(width, 300)
        self.binary_height = max(height, 200)

        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        output_vid = Path(config.file_manager.new_folderpath, "output.avi")
        self.out = cv2.VideoWriter(str(output_vid), fourcc, 50.0, (self.width, self.height))

        self.bin_stock = np.zeros((self.binary_height, self.binary_width))
        self.bin_P = self.bin_stock.copy()
        self.bin_CR = self.bin_stock.copy()
        #self.CRStock = self.bin_stock.copy()

        self.src_txt = np.zeros((20, width, 3))
        self.prev_txt = self.src_txt.copy()
        cv2.putText(self.src_txt, 'Source', (15, 12), font, .7, (255, 255, 255), 0, cv2.LINE_4)
        cv2.putText(self.prev_txt, 'Preview', (15, 12), font, .7, (255, 255, 255), 0, cv2.LINE_4)
        cv2.putText(self.prev_txt, 'EyeLoop', (width - 50, 12), font, .5, (255, 255, 255), 0, cv2.LINE_8)

        self.bin_stock_txt = np.zeros((20, self.binary_width))
        self.bin_stock_txt_selected = self.bin_stock_txt.copy()
        self.crstock_txt = self.bin_stock_txt.copy()
        self.crstock_txt[0:1, 0:self.binary_width] = 1
        self.crstock_txt_selected = self.crstock_txt.copy()

        cv2.putText(self.bin_stock_txt, 'P | R/F | T/G || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)
        cv2.putText(self.bin_stock_txt_selected, '(*) P | R/F | T/G || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)

        cv2.putText(self.crstock_txt, 'CR | W/S | E/D || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)
        cv2.putText(self.crstock_txt_selected, '(*) CR | W/S | E/D || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)

        cv2.imshow("CONFIGURATION", np.hstack((self.bin_stock, self.bin_stock)))
        cv2.imshow("BINARY", np.vstack((self.bin_stock, self.bin_stock)))

        cv2.moveWindow("BINARY", 105 + width * 2, 100)
        cv2.moveWindow("CONFIGURATION", 100, 100)

        cv2.imshow("Tool tip", self.first_tool_tip)

        cv2.moveWindow("Tool tip", 100, 1000 + height + 100)
        try:
            cv2.setMouseCallback("CONFIGURATION", self.mousecallback)
            cv2.setMouseCallback("Tool tip", self.tip_mousecallback)
        except:
            print("Could not bind mouse-buttons.")

    def place_cross(self, source: np.ndarray, point: tuple, color: tuple) -> None:
        try:
            source[to_int(point[1] - 3):to_int(point[1] + 4), to_int(point[0])] = color
            source[to_int(point[1]), to_int(point[0] - 3):to_int(point[0] + 4)] = color
        except:
            pass


    def update_record(self, frame_preview) -> None:
        cv2.imshow("Recording", frame_preview)
        if cv2.waitKey(1) == ord('q'):
            config.engine.release()

    def skip_track(self):
        self.update = self.real_update


    def pupil(self, source_rgb):
        try:
            pupil_center, pupil_width, pupil_height, pupil_angle = self.pupil_processor.fit_model.params

            cv2.ellipse(source_rgb, tuple_int(pupil_center), tuple_int((pupil_width, pupil_height)), pupil_angle, 0, 360, red, 1)
            self.place_cross(source_rgb, pupil_center, red)
            return True
        except Exception as e:
            logger.info(f"pupil not found: {e}")
            return False

    def cr_1(self, source_rgb):
        try:
            #cr_center, cr_width, cr_height, cr_angle = params = self.cr_processor_1.fit_model.params

            #cv2.ellipse(source_rgb, tuple_int(cr_center), tuple_int((cr_width, cr_height)), cr_angle, 0, 360, green, 1)
            self.place_cross(source_rgb, self.cr_processor_1.center, green)
            return True
        except Exception as e:
            logger.info(f"cr1 func: {e}")
            return False

    def cr_2(self, source_rgb):
        try:
            #cr_center, cr_width, cr_height, cr_angle = params = self.cr_processor_2.fit_model.params

            #cv2.ellipse(source_rgb, tuple_int(cr_center), tuple_int((cr_width, cr_height)), cr_angle, 0, 360, green, 1)
            self.place_cross(source_rgb, self.cr_processor_2.center, green)
            return True
        except Exception as e:
            logger.info(f"cr2 func: {e}")
            return False

    def adj_update(self, img):
        source_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        #if self.pupil_(source_rgb):
        self.bin_P = self.bin_stock.copy()

        if self.pupil_(source_rgb):
            self.bin_P[0:20, 0:self.binary_width] = self.bin_stock_txt_selected
        else:
            self.bin_P[0:20, 0:self.binary_width] = self.bin_stock_txt

        #self.bin_CR = self.bin_stock.copy()

        try:
            pupil_area = self.pupil_processor.source

            offset_y = int((self.binary_height - pupil_area.shape[0]) / 2)
            offset_x = int((self.binary_width - pupil_area.shape[1]) / 2)
            self.bin_P[offset_y:min(offset_y + pupil_area.shape[0], self.binary_height),
            offset_x:min(offset_x + pupil_area.shape[1], self.binary_width)] = pupil_area
        except:
            pass

        self.cr1_(source_rgb)
        self.cr2_(source_rgb)

        self.bin_CR = self.bin_stock.copy()

        try:
            cr_area = self.current_cr_processor.source
            offset_y = int((self.binary_height - cr_area.shape[0]) / 2)
            offset_x = int((self.binary_width - cr_area.shape[1]) / 2)
            self.bin_CR[offset_y:min(offset_y + cr_area.shape[0], self.binary_height),
            offset_x:min(offset_x + cr_area.shape[1], self.binary_width)] = cr_area
            self.bin_CR[0:20, 0:self.binary_width] = self.crstock_txt_selected
        except:
            self.bin_CR[0:20, 0:self.binary_width] = self.crstock_txt
            pass




        #print(cr_area)

        cv2.imshow("BINARY", np.vstack((self.bin_P, self.bin_CR)))
        cv2.imshow("CONFIGURATION", source_rgb)
        #self.out.write(source_rgb)

        self.key_listener(cv2.waitKey(50))
        if self.first_run:
            cv2.destroyAllWindows()
            self.first_run = False


    def real_update(self, img) -> None:
        source_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        self.pupil_(source_rgb)
        self.cr1_(source_rgb)
        self.cr2_(source_rgb)

        cv2.imshow("TRACKING", source_rgb)

        threading.Timer(self.fps, self.skip_track).start() #run feed every n secs (n=1)
        self.update = lambda _: None

        if cv2.waitKey(1) == ord("q"):


            config.engine.release()

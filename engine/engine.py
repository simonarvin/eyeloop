import cv2
import time
import numpy as np

import config
from engine.processor import Shape
from constants.engine_constants import *
from utilities.general_operations import to_int, tuple_int
import matplotlib.pyplot as plt

class Engine:
    def __init__(self, eyeloop):

        self.live = True #Access this to check if Core is running.

        self.eyeloop = eyeloop
        self.model = config.arguments.model  #   Used for assigning appropriate circular model.

        if config.arguments.markers == False:  #   Markerless. -m 0 (default)
            self.place_markers = lambda: None
        else:                           #   Enables markers to remove artifacts. -m 1
            self.place_markers = self.real_place_markers
        self.marks          =   []

        if config.arguments.tracking == 0:   #   Recording mode. --tracking 0
            self.iterate = self.record
        else:                       #   Tracking mode. --tracking 1 (default)
            self.iterate = self.track

        self.angle = 0
        self.extractors = []

        self.std            =   -1  #    Used for infering blinking.
        self.mean           =   -1  #    Used for infering blinking.

        max_cr_processor    =   3
        self.cr_processors  =   [Shape(type = 2) for _ in range(max_cr_processor)]
        self.pupil_processor=   Shape()

        #   Via "gui", assign "refresh_pupil" to function "processor.refresh_source"
        #   when the pupil has been selected.
        self.refresh_pupil  =   lambda x: None

    def load_extractors(self, extractors:list = []) -> None:
        self.extractors = extractors

    def real_place_markers(self) -> None:
        """
        Circumvents artifacts (crudely) via demarcations for the pupil processor.
        """

        for i, mark in enumerate(self.marks):
            if (i % 2) == 0:
                try:
                    self.pupil_processor.area[mark[1]-self.pupil_processor.corners[0][1]:self.marks[i+1][1]-self.pupil_processor.corners[0][1],
                    mark[0]-self.pupil_processor.corners[0][0]:self.marks[i+1][0]-self.pupil_processor.corners[0][0]]=100
                except:
                    #odd marks or no pupil yet.
                    break

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
        "time" : timestamp,
        "frame" : config.importer.frame,
        "blink" : -1,
        "cr_dim" : -1,
        "cr_cen" : -1,
        "cr_ang" : -1,
        "pupil_dim" : -1,
        "pupil_cen" : -1,
        "pupil_ang" : -1
        }

        config.graphical_user_interface.update_record(self.source)

        self.run_extractors()


    def arm(self, width, height, image) -> None:
        self.norm = (width + height) * .003
        self.norm_cr_artefact = int(6 * self.norm)
        self.blink_mean=0
        self.mean=np.mean(image)
        self.base_mean = -1
        self.blink = 0
        self.means=[]
        self.means_x=[]
        self.blink_i = 0

        self.width, self.height = width, height
        config.graphical_user_interface.arm(width, height)

        self.update_feed(image)

        self.pupil_processor.binarythreshold = float(np.min(self.source))*.7
        for cr_processor in self.cr_processors:
            cr_processor.binarythreshold = float(np.min(self.source))*.7

    def check_blink(self, threshold = 5) -> bool:
        """
        Analyzes the monochromatic distribution of the frame,
        to infer blinking. Change in mean during blinking is very distinct.
        """

        mean            = np.mean(self.source)
        delta = self.mean - mean
        self.mean=mean
        self.means.append(mean)
        self.means_x.append(len(self.means_x))
    #    print("delta", delta)
        if abs(delta) > 1.3:
            self.blink = 10
            print("blink!")
            return False
        elif self.blink != 0:

            self.blink -= 1
            return False
        self.blink=0


        return True

    def track(self) -> None:
        """
        Executes the tracking algorithm on the pupil and corneal reflections.
        First, blinking is analyzed.
        Second, corneal reflections are detected.
        Third, corneal reflections are inverted at pupillary overlap.
        Fourth, pupil is detected.
        Finally, data is logged and extractors are run.
        """

        timestamp = time.time()
        cr_width = cr_height = cr_center = cr_angle = pupil_center = pupil_width = pupil_height = pupil_angle = -1
        blink = 0

        if self.check_blink():
            try:
                pupil_area = self.pupil_processor.area
                offsetx, offsety = -self.pupil_processor.corners[0]
            except:
                offsetx, offsety = 0, 0
                _, pupil_area = cv2.threshold(cv2.GaussianBlur(self.pupil_source, (self.pupil_processor.blur, self.pupil_processor.blur), 0), 60 + self.pupil_processor.binarythreshold, 255, cv2.THRESH_BINARY_INV)

            for cr_processor in self.cr_processors:
                if cr_processor.active:
                    cr_processor.refresh_source(self.source)

                    if cr_processor.track():
                        self.cr_artifacts(cr_processor, offsetx, offsety, pupil_area)
                        cr_center, cr_width, cr_height, cr_angle, cr_dimensions_int = cr_processor.ellipse.parameters()

            self.refresh_pupil(self.pupil_source) #lambda _: None when pupil not selected in gui.
            self.place_markers() #lambda: None when markerless (-m 0).

            if self.pupil_processor.track():
                self.pupil = self.pupil_processor.center
                pupil_center, pupil_width, pupil_height, pupil_angle, pupil_dimensions_int = self.pupil_processor.ellipse.parameters()
                self.base_mean = np.mean(self.source)

        else:
            blink = 1
        self.blink_i = blink

        try:
            config.graphical_user_interface.update_track(blink)
        except Exception as e:
            print("Error! Did you assign the graphical user interface (GUI) correctly?")
            print("Error message: ", e)
            self.release()
            return



        self.dataout = {
        "time" : timestamp,
        "frame" : config.importer.frame,
        "blink" : blink,
        "cr_dim" : (cr_width, cr_height),
        "cr_cen" : cr_center,
        "cr_ang" : cr_angle,
        "pupil_dim" : (pupil_width, pupil_height),
        "pupil_cen" : pupil_center,
        "pupil_ang" : pupil_angle
        }

        self.run_extractors()

    def activate(self) -> None:
        """
        Ativates all extractors.
        The extractor activate() function is optional.
        """

        for extractor in self.extractors:
            try:
                extractor.activate()
            except:
                pass

    def release(self) -> None:
        """
        Releases/deactivates all running process, i.e., importers, extractors.
        """

        self.live = False
        plt.plot(self.means_x[1:], np.diff(self.means))
        plt.show()

        try:
            config.importer.release()
        except:
            pass

        for extractor in self.extractors:
            try:
                extractor.release()
            except:
                pass


    def update_feed(self, img) -> None:

        self.source = img.copy()
        self.pupil_source = img.copy()

        self.iterate()

    def cr_artifacts(self, cr_processor, offsetx:int, offsety:int, pupil_area) -> None:
        """
        Computes pupillary overlaps and acts to remove these artifacts.
        """

        cr_center, cr_width, cr_height, cr_angle, cr_dimensions_int = cr_processor.ellipse.parameters()

        cr_center_int = tuple_int(cr_center)
        larger_width, larger_height = larger_radius = tuple(int(1.2 * element) for element in cr_dimensions_int)

        cr_width_norm = larger_width  * self.norm
        cr_height_norm = larger_height * self.norm

        dimensional_product = larger_width * larger_height

        arc = [dimensional_product / np.sqrt((cr_width_norm * anglesteps_cos[i])**2 + (cr_width_norm * anglesteps_sin[i])**2) for i in angular_range]
        cos_sin_arc = [(to_int(anglesteps_cos[i] * arc[i]), to_int(anglesteps_sin[i] * arc[i])) for i in angular_range]

        hit_list = zeros.copy()

        for i, arc_element in enumerate(cos_sin_arc):
            cos, sin = arc_element
            x = cr_center_int[0] + offsetx + cos
            y = cr_center_int[1] + offsety + sin
            n=1


            while n < self.norm_cr_artefact:
                n+=1
                try:
                    if pupil_area[y, x] != 0:
                        hit_list[i] = i + 1
                        break
                    else:
                        x += cos
                        y += sin
                except:
                    break


        if np.any(hit_list):
            delta = np.count_nonzero(number_row - hit_list)

            if delta < self.norm_cr_artefact:

                cv2.ellipse(self.pupil_source, cr_center_int, larger_radius, cr_angle, 0, 360, 0, -1)
            else:

                for element in hit_list:
                    if element != 0:
                        cos, sin = cos_sin_arc[element - 1]
                        x = cr_center_int[0] + cos
                        y = cr_center_int[1] + sin
                        cv2.ellipse(self.pupil_source, cr_center_int, larger_radius, cr_angle, element * 40-40, element*40, 0, 4) #normalize qqqq
                        #cv2.line(self.pupil_source, cr_center_int, (x, y), 0, 4) #normalize linewidth qqqq

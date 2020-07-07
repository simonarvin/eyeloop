import cv2
import numpy as np
from engine.models.ellipsoid import Ellipse
from engine.models.circular import Circle
from utilities.general_operations import to_int, distance, tuple_int
from constants.processor_constants import *
import config

class Shape():
    def __init__(self, type=1):

        self.active             = False
        self.center             =   -1
        self.margin             =   -1
        self.walkout_offset     =   0
        self.binarythreshold    =   -1
        self.blur               =   9
        self.type               =   type
        self.cropsource         =   -1
        self.corners            =   -1
        self.center_index       =   0
        self.model              =   config.arguments.model
        self.walkout            =   Contour(self, type)

        self.parameters         =   0

        if type == 1:
            self.thresh = self.pupil_thresh

            if self.model == "circular":
                self.fit_model = Circle(self)
            else:
                self.fit_model = Ellipse(self)

        else:
            self.fit_model = Ellipse(self)

            self.thresh = self.cr_thresh

    def pupil_thresh(self):
        #Pupil
        _, self.area = cv2.threshold(self.area, 50 + self.binarythreshold, 255, cv2.THRESH_BINARY_INV)

    def cr_thresh(self):
        #CR
        _, self.area = cv2.threshold(self.area, 150 + self.binarythreshold, 255, cv2.THRESH_BINARY)

    def refresh_source(self, source):

        try:
            self.cropsource         =   source[self.corners[0][1]:self.corners[1][1],
            self.corners[0][0]:self.corners[1][0]]

            #The following lines perform a simple binarization and apply a smoothing gaussian kernel.
            self.area       =   self.cropsource.copy()
            if self.type==1:

                erosion = cv2.erode(self.area, kernel,iterations = 2)

                self.area       =   cv2.GaussianBlur(erosion, (self.blur, self.blur), 0)

            else:
                self.area       =   cv2.GaussianBlur(self.area, (self.blur, self.blur), 0)
            self.thresh()

        except:# Exception as e:
            pass

    def reset(self, center, col):
        self.active         = True
        self.margin         =   0
        self.walkout_offset =   0
        self.center         =   center

        mesh                =   np.array(np.meshgrid([0, 5, -5], [0, -5, 5]))
        point_offset        =   mesh.T.reshape(-1, 2)
        self.original_center=   [(center[0] + p[0], center[1] + p[1]) for p in point_offset]

        self.standard_corners   =   [(0, 0), (config.engine.width, config.engine.height)]
        self.corners        =   self.standard_corners.copy()

    def track(self):

        try:
            center = [self.center[0] - self.corners[0][0], self.center[1] - self.corners[0][1]]
            walkout = self.walkout
            walkout.reset(center)
            fit_product = 1
            if walkout.walkout():

                fit_product = self.fit_model

                if fit_product.fit(walkout.rx, walkout.ry):
                    ellipse            =   fit_product
                else:
                    ellipse = 0
            else:
                ellipse = 0

        except Exception as e:
            return False

        if ellipse == fit_product:

            center, width, height   =   ellipse.center, ellipse.width, ellipse.height

            # if self.type == 2:
            #     if distance(np.array(center), np.array(self.center)) > 6: #normalize qqqq
            #         self.center = self.original_center[self.center_index]
            #         self.corners        =   self.standard_corners.copy()
            #         return False

            self.ellipse = ellipse
            self.center = center

            #"walkout_offset" defines the walkout offset for the next frame.
            #The multiplication factor, here .4, returns slightly below the average.
            self.walkout_offset    =   int(.4*(width + height))

            self.margin = np.amax(ellipse.dimensions_int) * 3
            center_int = tuple_int(center)

            self.corners[0] = (max(center_int[0] - self.margin, 0), max(center_int[1] - self.margin, 0))
            self.corners[1] = (min(center_int[0] + self.margin, config.engine.width), min(center_int[1] + self.margin, config.engine.height))

            self.center_index = 0
            return True
        else:
            #   Shape detection failed. We reset the crop area and iterate through a list of alternative center points.

            self.center         = self.original_center[self.center_index] # This loops through a list with centers surrounding the origin.
            self.corners        = self.standard_corners.copy()
            self.walkout_offset = 0

            if self.center_index < 8:
                self.center_index += 1
                self.track()
            else:
                self.center_index = 0
                return False

stdthres = 1
center_stdthres = .95
class Contour:

    def __init__(self, processor, type):

        self.processor      =   processor
        if type == 2:
            self.filter = lambda a, b, c, _: (a,b,c)
        else:
            if processor.model == "circular":
                self.filter = self.circular_filter
            else:
                self.filter = self.ellipsoid_filter


    def reset(self, center):
        self.center         =   center
        self.rx             =   -1
        self.ry             =   -1
        self.fit            =   -1

    def ellipsoid_filter(self, x, y, coord_length, step_list):
        # REVISE THIS QQQQ
        neighbor_distances = np.abs(np.diff(step_list))

        neighbor_std     =   np.std(neighbor_distances)
        neighbor_mean    =   np.mean(neighbor_distances)

        lowerlimit = max(neighbor_mean - neighbor_std * stdthres, 0)
        upperlimit = max(neighbor_mean + neighbor_std * stdthres, 2)

        #print(lowerlimit, upperlimit, neighbor_distances)

        for i, distance in enumerate(neighbor_distances):
            if distance > upperlimit:
                coord_length -= 1
                x[i] = 0
                y[i] = 0

        return x, y, coord_length

    def circular_filter(self, x, y, coord_length, step_list):

        center_std      = max(np.ceil(np.std(step_list) * center_stdthres), 3)
        center_mean     = int(np.mean(step_list))

        lowerlimit = center_mean - center_std
        upperlimit = center_mean + center_std

        for i, step in enumerate(step_list):
            if ~(lowerlimit < step <  upperlimit):
                coord_length -= 1
                x[i] = 0
                y[i] = 0
        return x, y, coord_length


    def walkout(self, total_n=0):
        """
        Points are iteratively translated centrifugally to a limit,
        and in an equally distributed manner (θ=360/n) from a center.
        Notably, n is offset based on the width and height of the previously detected ellipsoid.

        Similar to what was described by Sakatani and Isa (2004).
        """

        x              =   point_source.copy()
        y              =   point_source.copy()
        step_list      =   step_list_source.copy()

        offset         =   self.processor.walkout_offset

        for i, cos_sin in enumerate(cos_sin_steps):

            cos, sin = cos_sin

            x[i]       =   self.center[0] + cos * offset
            y[i]       =   self.center[1] + sin * offset

            insidemark = False

            for _ in limit:

                #If walkout coordinate hits out-of-contour area, break out of the loop.
                try:
                    pixel = self.processor.area[to_int(y[i]), to_int(x[i])]

                    if pixel != 255:
                        if pixel == 100: #inside mark
                            if insidemark == False:
                                lastcoord = x[i], y[i]
                                insidemark = True

                        else:
                            if insidemark:
                                x[i], y[i] = lastcoord

                            break
                    else:
                        insidemark = False

                except:
                    #Walkout hit outside of Processor area. Go back to previous in-bounds point, then break.
                    x[i]    -=  cos
                    y[i]    -=  sin
                    step_list[i] -=  1
                    break

                x[i]    += cos
                y[i]    += sin
                step_list[i] += 1

        coord_length = len(x)

        if coord_length < 5:
            return False

        x, y, coord_length = self.filter(x, y, coord_length, step_list)

        if coord_length < 4:
            return False

        self.rx, self.ry = x[(0 != x)], y[(0 != y)]

        return True

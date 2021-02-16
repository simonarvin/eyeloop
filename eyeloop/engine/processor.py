import cv2

import eyeloop.config as config
from eyeloop.constants.processor_constants import *
from eyeloop.engine.models.circular import Circle
from eyeloop.engine.models.ellipsoid import Ellipse
from eyeloop.utilities.general_operations import to_int, tuple_int
import time
import logging

from scipy.spatial.distance import cdist
logger = logging.getLogger(__name__)

"""
TODO:
XXFilter rx, ry
XXSingularize area/source
XXConvert CR artefact algorithm to matrix method
---If pupil not detected, choose from meshgrid centers
Infer blinking
Fail proof centerfinding. F.eks., gæt hvor pupillen nu er. Eller brug findcontour og find central contourcentrum
    forbedr dette
Overvej at tilføje cropping alligevel; Måske specifikt ved Gaussian/erosion.
Tilføj walkout offset
    ...du kan gøre det ved at lave en mask i centrum

Ryk extractors core til class: self.core
    ligegyldigt da threading variable skal være pickable
Lav evt en extractor super-class

XX Tilpas ellipse modellen til det nye
    XX Optimér ellipse modellen

Forbedr clipping

Lav walkout til pupil og CR. CR med færre punkter

"""

class Center_class():
    def fit(self, r):
        self.params = tuple(np.mean(r, axis = 0))
        return self.params

class Shape():
    def __init__(self, type = 1, n = 0):

        self.active = False
        self.center = -1

        self.walkout_offset = 0

        self.binarythreshold = -1
        self.blur = (3, 3)
        self.type = type
        self.fit_ = lambda: None

        self.model = config.arguments.model
        self.type_entry = None
        self.track = lambda x:None


        if type == 1:
            self.artefact = lambda _:None
            self.type_entry = "pupil"
            self.thresh = self.pupil_thresh

            if self.model == "circular":
                self.fit_model = Circle(self)
            else:
                self.fit_model = Ellipse(self)

            self.min_radius = 3
            self.max_radius = 30 #change according to video size or argument
            self.cond = self.cond_
            #self.clip = lambda x:None
            self.clip = self.clip_
            self.center_adj = self.center_adj_
            self.walkout = self.pupil_walkout
        else:
            self.walkout = self.cr_walkout
            self.type_entry = f"cr_{n}"
            self.center_adj = lambda:None
            self.cond = lambda r,_:r
            self.clip = self.clip_
            self.expand = 1.2
            self.artefact = lambda _:None
            #self.artefact = self.artefact_
            self.fit_model = Center_class()#Circle(self)

            self.min_radius = 2
            self.max_radius = 5 #change according to video size or argument

            self.thresh = self.cr_thresh

    def pupil_thresh(self):
        # Pupil

        self.source[:] = cv2.threshold(cv2.GaussianBlur(cv2.erode(self.source, kernel, iterations = 1), self.blur, 0), self.binarythreshold, 255, cv2.THRESH_BINARY_INV)[1]
        #self.source[:] = cv2.GaussianBlur(self.source, self.blur, 0)

    def cr_thresh(self):
        # CR

        _, self.source[:] = cv2.threshold(cv2.GaussianBlur(self.source, self.blur, 0), self.binarythreshold, 255, cv2.THRESH_BINARY)
        #self.source[:] =

    def reset(self, center):

        self.active = True
        self.margin = 0
        self.walkout_offset = 0
        self.center = center
        self.fit_ = self.fit
        self.track = self.track_

        self.standard_corners = [(0, 0), (config.engine.width, config.engine.height)]
        self.corners = self.standard_corners.copy()

        #self.tracker = cv2.TrackerMedianFlow_create()

    def track_(self, source):

        self.source = source.copy()
        #self.img = img

        # Performs a simple binarization and applies a smoothing gaussian kernel.
        self.thresh() #either pupil or cr
        self.fit_() #gets fit model


    def center_adj_(self):
        return
        #revise, todo
        circles = cv2.HoughCircles(self.source, cv2.HOUGH_GRADIENT,1,20,
                            param1=50,param2=30,minRadius=self.minRadius,maxRadius=self.maxRadius)
        contour_center = config.engine.center
        self.center = circles[0,0][:1]




    def artefact_(self, params):
        cv2.circle(config.engine.pup_source, tuple_int(params[0]), to_int(params[1] * self.expand), black, -1)

    def fit(self):
        try:
            r = self.walkout()

            self.center = self.fit_model.fit(r)

            #params = self.fit_model.params
            #self.artefact(params)

            config.engine.dataout[self.type_entry] = self.fit_model.params#params
        except IndexError:
            logger.info(f"fit indexrror")
            self.center_adj()
        except Exception as e:
            logger.info(f"fit-func error: {e}")


    def cond_(self, r, crop_list):


        #t=time.time()
        #print(np.mean([rx,ry],axis=1, dtype=np.float64).shape)
    #    dists =  np.linalg.norm(np.mean([rx,ry],axis=1, dtype=np.float64)[:,np.newaxis] - np.array([rx, ry], dtype = np.float64), axis = 0)
        dists =  np.linalg.norm(np.mean(r,  axis = 0,dtype=np.float64) - r, axis = 1)

        #print(time.time() - t)
        #
        mean_ = np.mean(dists)
        std_ = np.std(dists)
        #t=time.time()
        lower, upper = mean_ - std_, mean_ + std_ * .8
        cond_ = np.logical_and(np.greater_equal(dists, lower), np.less(dists, upper))
        #print(time.time() - t)
    #    print(cond_, dists)
        return r[cond_]

    def clip_(self, crop_list):
        np.clip(crop_list, self.min_radius, self.max_radius, out = crop_list)

    def pupil_walkout(self):


        #diag_matrix = main_diagonal[:canvas_.shape[0], :canvas_.shape[1]]

        try:
            center = np.array(self.center, dtype=int)
        except:
            #nonetype

            return
        canvas = np.array(self.source, dtype=int)#.copy()

        r = rr_2d.copy()

        crop_list = crop_stock.copy()


        canvas_ = canvas[center[1]:, center[0]:]
        canv_shape0, canv_shape1 = canvas_.shape
        crop_canvas = np.flip(canvas[:center[1], :center[0]])
        crop_canv_shape0, crop_canv_shape1 = crop_canvas.shape

        crop_canvas2 = np.fliplr(canvas[center[1]:, :center[0]])
        crop_canv2_shape0, crop_canv2_shape1 = crop_canvas2.shape

        crop_canvas3 = np.flipud(canvas[:center[1], center[0]:])###
        crop_canv3_shape0, crop_canv3_shape1 = crop_canvas3.shape

        canvas2 = np.flip(canvas) # flip once


        crop_list=np.array(np.argmax(np.array(
        [
        canvas_[:, 0][self.min_radius:self.max_radius] == 0, canvas_[0, :][self.min_radius:self.max_radius] == 0,canvas_[main_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas[main_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[main_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas3[main_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,canvas2[-center[1], -center[0]:][self.min_radius:self.max_radius] == 0,canvas2[-center[1]:, -center[0]][self.min_radius:self.max_radius] == 0,
        canvas_[ half_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas[half_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[half_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas3[half_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,canvas_[invhalf_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas[invhalf_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[invhalf_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas3[invhalf_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,canvas_[fourth_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas3[fourth_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas[fourth_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[fourth_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,canvas_[invfourth_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas2[invfourth_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas[invfourth_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas3[invfourth_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,
        canvas_[third_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[third_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas[third_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas3[third_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0,canvas_[invthird_diagonal[:canv_shape0, :canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas2[invthird_diagonal[:crop_canv2_shape0, :crop_canv2_shape1]][self.min_radius:self.max_radius] == 0,
        crop_canvas[invthird_diagonal[:crop_canv_shape0, :crop_canv_shape1]][self.min_radius:self.max_radius] == 0,crop_canvas3[invthird_diagonal[:crop_canv3_shape0, :crop_canv3_shape1]][self.min_radius:self.max_radius] == 0
        ], dtype = bool
        ), axis=1),dtype=int) + self.min_radius


        #simple:

        r[:8,:] = center
        r[ry_add, 1] += crop_list[ry_add]
        r[rx_add, 0] += crop_list[rx_add]
        r[ry_subtract, 1] -= crop_list[ry_subtract] #
        r[rx_subtract, 0] -= crop_list[rx_subtract]
        r[rx_multiplied, 0] *= rx_multiply
        r[ry_multiplied, 1] *= ry_multiply
        r[8:,:] += center


        # try:
        #    canvas_rgb = cv2.cvtColor(self.source, cv2.COLOR_GRAY2RGB)
        #    cy, cx = np.mean(ry, dtype=int), np.mean(rx, dtype=int)
        #    canvas_rgb[cy,cx] = [0,0,255]
        #    canvas_rgb[ry.astype("int"), rx.astype("int")] = [0,0,255]
        #    canvas_rgb[center[1], center[0]] = [255,0,0]
        #    rx1,ry1 = self.cond(rx, ry, crop_list)
        #    canvas_rgb[ry1.astype("int"), rx1.astype("int")] = [0,255,0]
        #    cv2.imshow("JJJ", canvas_rgb)
        #    cv2.waitKey(5)
        # except Exception as e:
        #    print(e)


        return self.cond(r, crop_list)#rx[cond_], ry[cond_]#rx, ry

    def cr_walkout(self):


        #diag_matrix = main_diagonal[:canvas_.shape[0], :canvas_.shape[1]]

        try:
            center = np.array(self.center, dtype=int)
        except:
            #nonetype

            return
        #canvas = np.array(self.source, dtype=int)#.copy()

        r = rr_2d_cr.copy()


        crop_list = crop_stock_cr.copy()
        #rx = np.zeros(4)
        #ry = np.zeros(4)

        canvas_ = self.source[center[1]:, center[0]:]

        crop_list[0] = np.argmax(canvas_[:, 0] == 0) #- 1
        #crop_ = np.argmax(canvas_[:, 0] == 0) #- 1

        #ry[0], rx[0] = crop_ + center[1], center[0]


        crop_list[2] = np.argmax(canvas_[0, :] == 0) #- 1
        #crop_ = np.argmax(canvas_[0, :] == 0) #- 1

    #    ry[2], rx[2] = center[1], crop_ + center[0]


        canvas = np.flip(self.source) # flip once

        crop_list[3] = -np.argmax(canvas[-center[1], -center[0]:] == 0)# - 1
        #crop_ = np.argmax(canvas[-center[1], -center[0]:] == 0)# - 1

        #ry[3], rx[3] = center[1], -crop_ + center[0]


        crop_list[1]= -np.argmax(canvas[-center[1]:, -center[0]] == 0) #- 1
    #    crop_ = np.argmax(canvas[-center[1]:, -center[0]] == 0)

        #ry[1], rx[1] = -crop_ + center[1], center[0]
        #print()

        #print(r, crop_list)
        r[:,:] = center
        r[:2, 1] += crop_list[:2]
        r[2:, 0] += crop_list[2:]
        #print(r, rx, ry)

        # try:
        #
        #    canvas_rgb = cv2.cvtColor(self.source, cv2.COLOR_GRAY2RGB)
        #
        #   # canvas_rgb[cy,cx] = [0,0,255]
        #    canvas_rgb[ry.astype("int"), rx.astype("int")] = [0,255,0]
        #    canvas_rgb[r[:,1].astype("int"), r[:,0].astype("int")] = [0,0,255]
        #    #canvas_rgb[center[1], center[0]] = [255,0,0]
        #    #rx1,ry1 = self.cond(rx, ry, crop_list)
        #   # canvas_rgb[ry1.astype("int"), rx1.astype("int")] = [0,255,0]
        #    cv2.imshow("JJJ", canvas_rgb)
        #    cv2.waitKey(5)
        # except Exception as e:
        #    print(e)

        return r#rx[cond_], ry[cond_]#rx, ry

import cv2
#import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing
ctx = multiprocessing.get_context("spawn")

import logging

logger = logging.getLogger(__name__)

class vis_stim:

    def __init__(self):
        self.x_ = -1080
        self.y_ = -1000
        self.height = int(500)
        self.width =  int(500)
        self.wait_fps = 10
        self.data_queue = []
        self.online = True
        self.queue = ctx.Queue()

        max_px_width = 1920
        screen_width = 62
        self.origin_=(0, 0)
        pixels_per_cm = max_px_width/screen_width

        eye_coord = {
        "y" : 20 * pixels_per_cm, #positive: right; negative: left
        "z" : 20 * pixels_per_cm, #positve: down; negative: up;
        "x" : 10 * pixels_per_cm  #away from screen
        }

        self.x = eye_coord["x"]
        self.resolution = 1
        self.square = True

        self.duration = 0
        self.protocol_step = 0
        self.orientation = 0
        self.temporal_freq = 0
        self.spatial_freq = 0
        self.inter_stim_duration = 1


        self.initial_pause = .1

        self.cos_or = 0
        self.sin_or = 0
        self.origin = (self.width, self.height)

        self.stock_mesh = np.meshgrid(np.arange(0, self.width, self.resolution) - eye_coord["y"], np.arange(0, self.height, self.resolution) - eye_coord["z"])
        self.reference = 0
        self.timer = 0
        self.a = 0

        self.inter_stim_canvas = np.zeros(self.origin).T

        self.PROTOCOL = self.load_protocol()
        self.fetch = lambda x: None

        #pg.init()
        #self.screen = pg.display.set_mode(self.origin)#, pg.DOUBLEBUF | pg.HWSURFACE | pg.FULLSCREEN)
        #self.clock = pg.time.Clock()
        #self.screen.fill((0,0,0))

        #cv2.namedWindow("canvas", cv2.WND_PROP_FULLSCREEN)
        #cv2.moveWindow("canvas",0,0)
        #cv2.namedWindow("canvas", cv2.WND_PROP_FULLSCREEN)



    def activate(self):
        print("Activating corrected visual stimulus..")
        self.reference = time.time()
        #cv2.setWindowProperty("canvas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        #cv2.namedWindow("canvas", cv2.WND_PROP_FULLSCREEN)
        #cv2.setWindowProperty("canvas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #cv2.moveWindow("canvas",self.x_, self.y_)
        #cv2.destroyWindow("canvas")
        self.fetch = self.ifetch


    def ifetch(self, core):

        current_time = time.time()
        self.timer = time.time() - self.reference

        core.dataout["vstim"] = {"state" : "PRESTIM"}
        cv2.namedWindow("canvas")
        cv2.moveWindow("canvas",self.x_,self.y_)
        cv2.imshow("canvas", self.inter_stim_canvas)
        cv2.waitKey(1)

        if self.timer >= self.initial_pause:
            print("initial pause ended,\nstarting trial")
            self.fetch = self.rfetch
            core.dataout["vstim"] = {"state" : "ACTIVATED"}
            cv2.destroyWindow("canvas")

            self.stim_thread = ctx.Process(target=self.stim, args=[self.queue])

            self.stim_thread.start()
            #self.stim_thread.join()
            #self.stim_thread = threading.Thread(target=self.stim)
        #    self.stim_thread.daemon = True
        #    self.stim_thread.start()

            return

        #cv2.imshow("canvas", self.inter_stim_canvas)

    def release(self):
        try:
            self.online = False
            #self.stim_thread.join()
        except:
            pass

    def stim(self, queue):
        #self.screen.fill((30, 30, 30))

        cv2.namedWindow("canvas")
        cv2.moveWindow("canvas",self.x_,self.y_)
        while self.online:

            current_time = time.time()
            self.timer = time.time() - self.reference

            if self.timer >= self.duration:
                if self.timer - self.duration <= self.inter_stim_duration:

                    queue.put({"state" : "INTERSTIM", "step" : self.protocol_step})

                    #cv2.imshow("canvas", self.inter_stim_canvas)
                    #print("B")
                    cv2.imshow("canvas", self.inter_stim_canvas)
                    cv2.waitKey(self.wait_fps)
                    #cv2.waitKey(1)
                    #self.screen.blit(self.inter_stim_canvas, self.origin_)
                    #pg.display.flip()
                    continue


                try:
                    params = self.PROTOCOL[self.protocol_step]
                except:
                    logger.info(f"vis-stim protocol ended;")

                    return

                self.reference = current_time
                self.timer = 0
                self.duration = params["duration"]
                self.temporal_freq = np.radians(params["temporal_freq"])
                orientation = np.radians(params["orientation"])
                self.spatial_freq = np.degrees(params["spatial_freq"])

                vertical_, horisontal_ = self.stock_mesh.copy()

                cos_or = np.cos(-orientation)
                sin_or = np.sin(-orientation)

                z_ = vertical_ * cos_or - horisontal_ * sin_or
                y_ = vertical_ * sin_or + horisontal_ * cos_or


                self.b = (np.pi/2 - np.arccos(z_/np.sqrt(self.x**2 + y_**2 + z_**2))) #+ np.arctan(-horisontal_/self.x)
                self.a = 2 * np.pi * self.spatial_freq
                #self.b *= -np.arctan(-horisontal_/self.x)

                #core.dataout["vis_stim_switch"] = params
                queue.put({"state" : "STIM", "step" : self.protocol_step, "params" : str(params)})

                self.protocol_step += 1


            #t = time.time()

            S = np.cos(self.a * (self.b - self.timer * self.temporal_freq))

            S_ = cv2.resize(S, self.origin)

            if self.square:
                _, S_ = cv2.threshold(S_, .5, 1, cv2.THRESH_BINARY)
            cv2.imshow("canvas", S_)
            cv2.waitKey(self.wait_fps)
            #ss=time.time()
            #S_ = pg.surfarray.make_surface(np.stack((np.array(S_).T * 255,) * 3, axis = -1))
            #print(time.time()-ss)
            #self.screen.blit(S_, self.origin_)
            #pg.display.flip()
            #self.clock.tick(self.fps)



    def load_protocol(self, static = True):
        if static:
            P = []
            or_list = np.arange(8) * 45
            for orientation in or_list:

                P.append({
                "orientation" : orientation, #degrees
                "temporal_freq" : 5,#5, # degree per second
                "spatial_freq" : 0.25,#0.05, #cycles per degree
                "duration" : 2 #in secs
                })
        else:
            P = np.load("file/path/here")

        return P

    def rfetch(self, core = None):

        while not self.queue.empty():
            core.dataout["vstim"] = self.queue.get()


        #print(f"fps: {int(1/(time.time() - t))}")

if __name__ == 'visstim':
    extractors_add = [vis_stim()]

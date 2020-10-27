import numpy as np


class Conversion_extractor:
    def __init__(self, type=1, animal: str = "mouse", angle=0, center=None, interfaces=None):
        self.angle = angle
        self.center = center
        self.animal = animal
        if animal == "mouse":
            self.effective_rotation_radius = 1.25  # mm mouse
            self.bulbucorneal_distance = 0.2  # mm
        elif animal == "marmoset":
            self.effective_rotation_radius = 3.4  # mm :marmoset https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1913220/
            self.bulbucorneal_distance = 2.1  # marmoset: https://pubmed.ncbi.nlm.nih.gov/8333154/

        elif animal == "human":
            self.effective_rotation_radius = 6.4  # human https://pubmed.ncbi.nlm.nih.gov/9293516/
            self.bulbucorneal_distance = 4.6  # human

        self.err_fraction = self.effective_rotation_radius / (
                    self.effective_rotation_radius - self.bulbucorneal_distance)

        if interfaces is None:
            interfaces = []
        self.interfaces = interfaces

        if type == 1 or type == "coordinates":  # coordinates
            self.fetch = self.coordinates
        elif type == 2 or type == "area":  # area
            self.fetch = self.area

    def rotate(self, point, ang, origin):
        """
        Rotate a point counterclockwise by an angle around an origin.

        The angle should be given in degrees
        """

        angle = np.radians(ang)
        # print(ang, angle)
        ox, oy = origin
        px, py = point

        qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
        qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)

        return (qx, qy)

    def to_angular(self, point1, point2):
        """
        Based on Sakatani et al. (2004)
        """
        try:

            x = (point2[0] - point1[0]) * self.err_fraction + point1[0]
        except:
            return

        y = (point2[1] - point1[1]) * self.err_fraction + point1[1]
        # rad=np.radians(((point1[0] - x)/self.effective_rotation_radius))

        ang_pos_hor = np.arcsin(np.clip(np.radians(((point1[0] - x) / self.effective_rotation_radius)), -1, 1))

        ang_pos_ver = np.arcsin(np.clip(np.radians(-(point1[1] - y) / self.effective_rotation_radius), -1, 1))

        return ang_pos_hor, ang_pos_ver

    def area(self, core):
        """
        Computes pupil area based on mathematical eye model.
        Method described in article [doi: QQQQ].
        """

        try:
            dataout = core.dataout
        except:
            # offline; core = offline dataout.
            dataout = core

        try:
            width, height = dataout["pupil"][0][0], dataout["pupil"][0][1]
            pupil, cornea = dataout["pupil"][1], dataout["cr"][1]
        except Exception as e:
            raise Exception(e)

        try:
            pupil_coordinate = self.to_angular(pupil, cornea)

            angular_width = self.to_angular((pupil[0] + width, pupil[1]), cornea)
            angular_height = self.to_angular((pupil[0], pupil[1] + height), cornea)

            extremes = (abs(angular_width[0] - pupil_coordinate[0]), abs(angular_height[1] - pupil_coordinate[1]))

            radius_1 = np.sin(extremes[0]) * self.effective_rotation_radius

            radius_2 = np.sin(extremes[1]) * self.effective_rotation_radius
            area_1 = np.pi * radius_2 ** 2
            area_2 = np.pi * radius_2 ** 2

            return np.nanmean([area_1, area_2])
        except:
            return float("nan")

    def coordinates(self, core):

        try:
            dataout = core.dataout
        except:
            # offline; core = offline dataout.
            dataout = core

        try:
            # print(dataout["pupil_cen"], dataout["cr_cen"])
            pupil, cornea = dataout["pupil"][1], dataout["cr"][1]

            # pupil = self.rotate(pupil, self.angle, self.center)
            # cornea = self.rotate(cornea, self.angle, self.center)

            return self.to_angular(pupil, cornea)
        except Exception as e:
            print(e)
            return float("nan")

        # for interface in self.interfaces:
        #    interface.fetch(ang_pos_hor, ang_pos_ver)

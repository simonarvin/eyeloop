# original script: https://github.com/AlliedToasters/circle-fit
# original script author: Michael Klear/AlliedToasters
# hyper-fit doi: https://doi.org/10.1016/j.csda.2010.12.012
# hyper-fit authors: Kenichi Kanatani & Prasanna Rangarajan

import numpy as np

from utilities.general_operations import tuple_int


class Circle:
    def __init__(self, processor) -> None:
        self.shape_processor = processor

    def fit(self, x: np.ndarray, y: np.ndarray) -> bool:

        try:
            x_coord, y_coord, radius, v = self.hyper_fit(x, y)
            if radius < 4:
                return False

            self.center = [self.shape_processor.corners[0][0] + x_coord, self.shape_processor.corners[0][1] + y_coord]
            self.width = self.height = radius

            self.dimensions_int = tuple_int((radius, radius))

        except:
            return False

        return True

    def parameters(self) -> tuple:
        # center, width, height, angle, dimensions
        return self.center, self.width, self.height, 0, self.dimensions_int

    def hyper_fit(self, x: np.ndarray, y: np.ndarray) -> tuple:
        """
        Fits coords to circle using hyperfit algorithm.
        Inputs:
            - coords, list or numpy array with len>2 of the form:
            [
        [x_coord, y_coord],
        ...,
        [x_coord, y_coord]
        ]
            or numpy array of shape (n, 2)
        Outputs:
            - xc : x-coordinate of solution center (float)
            - yc : y-coordinate of solution center (float)
            - R : Radius of solution (float)
            - residu : s, sigma - variance of data wrt solution (float)
        """
        X = np.array(x)  # np.array([x[0] for x in coords])
        Y = np.array(y)  # np.array([x[1] for x in coords])

        n = X.shape[0]

        mean_X = np.mean(X)
        mean_Y = np.mean(Y)
        Xi = X - mean_X
        Yi = Y - mean_Y
        Zi = Xi * Xi + Yi * Yi

        # compute moments
        Mxy = np.sum(Xi * Yi) / n
        Mxx = np.sum(Xi * Xi) / n
        Myy = np.sum(Yi * Yi) / n
        Mxz = np.sum(Xi * Zi) / n
        Myz = np.sum(Yi * Zi) / n
        Mzz = np.sum(Zi * Zi) / n

        # computing the coefficients of characteristic polynomial
        Mz = Mxx + Myy
        Cov_xy = Mxx * Myy - Mxy * Mxy
        Var_z = Mzz - Mz * Mz

        A2 = 4 * Cov_xy - 3 * Mz * Mz - Mzz
        A1 = Var_z * Mz + 4. * Cov_xy * Mz - Mxz * Mxz - Myz * Myz
        A0 = Mxz * (Mxz * Myy - Myz * Mxy) + Myz * (Myz * Mxx - Mxz * Mxy) - Var_z * Cov_xy
        A22 = A2 + A2

        # finding the root of the characteristic polynomial

        det = Cov_xy
        if det != 0:
            Xcenter = (Mxz * (Myy) - Myz * Mxy) / det / 2.
            Ycenter = (Myz * (Mxx) - Mxz * Mxy) / det / 2.
        else:
            return 0, 0, 0, 0

        x = Xcenter + mean_X
        y = Ycenter + mean_Y
        r = np.sqrt(abs(Xcenter ** 2 + Ycenter ** 2 + Mz))
        # s = self.sigma(coords,x,y,r)
        return x, y, r, 1

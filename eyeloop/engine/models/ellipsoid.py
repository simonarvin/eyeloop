import numpy as np

from utilities.general_operations import tuple_int

"""Demonstration of least-squares fitting of ellipses
    __author__ = "Ben Hammel, Nick Sullivan-Molina"
    __credits__ = ["Ben Hammel", "Nick Sullivan-Molina"]
    __maintainer__ = "Ben Hammel"
    __email__ = "bdhammel@gmail.com"
    __status__ = "Development"
    Requirements
    ------------
    Python 2.X or 3.X
    np
    matplotlib
    References
    ----------
    (*) Halir, R., Flusser, J.: 'Numerically Stable Direct Least Squares
        Fitting of Ellipses'
    (**) http://mathworld.wolfram.com/Ellipse.html
    (***) White, A. McHale, B. 'Faraday rotation data analysis with least-squares
        elliptical fitting'
"""


class Ellipse:
    def __init__(self, processor):
        self.shape_processor = processor

    def fit(self, x, y):
        """Least Squares fitting algor6ithm
        Theory taken from (*)
        Solving equation Sa=lCa. with a = |a b c d f g> and a1 = |a b c>
            a2 = |d f g>
        Args
        ----
        data (list:list:float): list of two lists containing the x and y data of the
            ellipse. of the form [[x1, x2, ..., xi],[y1, y2, ..., yi]]
        Returns
        ------
        coef (list): list of the coefficients describing an ellipse
           [a,b,c,d,f,g] corresponding to ax**2+2bxy+cy**2+2dx+2fy+g
        """

        # Quadratic part of design matrix [eqn. 15] from (*)
        try:
            D1 = np.mat(np.vstack([x ** 2, x * y, y ** 2])).T
            # Linear part of design matrix [eqn. 16] from (*)
            D2 = np.mat(np.vstack([x, y, np.ones(len(x))])).T

            # forming scatter matrix [eqn. 17] from (*)
            S1 = D1.T * D1
            S2 = D1.T * D2
            S3 = D2.T * D2

            # Constraint matrix [eqn. 18]
            C1 = np.mat('0. 0. 2.; 0. -1. 0.; 2. 0. 0.')

            # Reduced scatter matrix [eqn. 29]
            M = C1.I * (S1 - S2 * S3.I * S2.T)

            # M*|a b c >=l|a b c >. Find eigenvalues and eigenvectors from this equation [eqn. 28]
            eval, evec = np.linalg.eig(M)

            # eigenvector must meet constraint 4ac - b^2 to be valid.
            cond = 4 * np.multiply(evec[0, :], evec[2, :]) - np.power(evec[1, :], 2)
            a1 = evec[:, np.nonzero(cond.A > 0)[1]]
            # self.fitscore=eval[np.nonzero(cond.A > 0)[1]]

            # |d f g> = -S3^(-1)*S2^(T)*|a b c> [eqn. 24]
            a2 = -S3.I * S2.T * a1

            # eigenvectors |a b c d f g>
            self.coef = np.vstack([a1, a2])
            if self._save_parameters():
                return False

            return True
        except Exception as e:

            return False

    def _save_parameters(self):
        """finds the important parameters of the fitted ellipse

        Theory taken form http://mathworld.wolfram
        Args
        -----
        coef (list): list of the coefficients describing an ellipse
           [a,b,c,d,f,g] corresponding to ax**2+2bxy+cy**2+2dx+2fy+g
        Returns
        _______
        center (List): of the form [x0, y0]
        width (float): major axis
        height (float): minor axis
        phi (float): rotation of major axis form the x-axis in radians
        """

        # eigenvectors are the coefficients of an ellipse in general form
        # a*x^2 + 2*b*x*y + c*y^2 + 2*d*x + 2*f*y + g = 0 [eqn. 15) from (**) or (***)
        a = self.coef[0, 0]
        b = self.coef[1, 0] / 2.
        c = self.coef[2, 0]
        d = self.coef[3, 0] / 2.
        f = self.coef[4, 0] / 2.
        g = self.coef[5, 0]

        if (a - c) == 0:
            return True

        # finding center of ellipse [eqn.19 and 20] from (**)
        x0 = (c * d - b * f) / (b ** 2. - a * c)
        y0 = (a * f - b * d) / (b ** 2. - a * c)

        # Find the semi-axes lengths [eqn. 21 and 22] from (**)
        numerator = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
        denominator1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        denominator2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        width = np.sqrt(numerator / denominator1)
        height = np.sqrt(numerator / denominator2)

        phi = .5 * np.arctan((2. * b) / (a - c))

        self.center = [self.shape_processor.corners[0][0] + x0, self.shape_processor.corners[0][1] + y0]
        self.width = width
        self.height = height
        self.dimensions_int = tuple_int((width, height))

        self.angle = np.rad2deg(phi) % 360
        return False

    def parameters(self):
        # return (self.shape_processor.corners[0][0] + self.center[0], self.shape_processor.corners[0][1] + self.center[1]), self.width, self.height, self.phi
        return self.center, self.width, self.height, self.angle, self.dimensions_int  # This is local to crop area

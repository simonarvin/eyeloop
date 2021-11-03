import numpy as np
np.seterr('raise')

from eyeloop.utilities.general_operations import tuple_int

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
        self.params = None

    def fit(self, r):
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

        x, y = r[:,0], r[:,1]
        

        # Quadratic part of design matrix [eqn. 15] from (*)

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
        #a2 = -S3.I * S2.T * a1

        # eigenvectors |a b c d f g>
        self.coef = np.vstack([a1, -S3.I * S2.T * a1])


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

    #    if (a - c) == 0:
    #        return True

        # finding center of ellipse [eqn.19 and 20] from (**)
        af = a * f
        cd = c * d
        bd = b * d
        ac = a * c

        b_sq = b ** 2.
        z_ = (b_sq - ac)
        x0 = (cd - b * f) / z_#(b ** 2. - a * c)
        y0 = (af - bd) / z_#(b ** 2. - a * c)

        # Find the semi-axes lengths [eqn. 21 and 22] from (**)
        ac_subtr = a - c
        numerator = 2 * (af * f + cd * d + g * b_sq - 2 * bd * f - ac * g)
        denom = ac_subtr * np.sqrt(1 + 4 * b_sq / ac_subtr**2)
        denominator1, denominator2 = (np.array([-denom, denom], dtype=np.float64) - c - a) * z_

        width = np.sqrt(numerator / denominator1)
        height = np.sqrt(numerator / denominator2)

        phi = .5 * np.arctan((2. * b) / ac_subtr)
        self.params = ((x0, y0), width, height, np.rad2deg(phi) % 360)

        #self.center, self.width, self.height, self.angle = self.params
        return self.params[0]

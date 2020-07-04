import numpy as np

angular_iter        =   9
angular_range       =   np.arange(angular_iter, dtype=np.int8)
number_row          =   np.arange(1, 10, 1)
anglesteps_cos      =   np.array([np.cos(np.radians(i * 40)) for i in angular_range], dtype=np.float64)
anglesteps_sin      =   np.array([np.sin(np.radians(i * 40)) for i in angular_range], dtype=np.float64)
zeros               =   np.zeros(9, dtype=int)

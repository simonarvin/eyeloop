import numpy as np

angular_iter = 12
angular_range = np.arange(angular_iter, dtype=np.int8)

anglesteps_cos = np.array([np.cos(np.radians(i * 360 / angular_iter)) for i in angular_range], dtype=np.float64)
anglesteps_sin = np.array([np.sin(np.radians(i * 360 / angular_iter)) for i in angular_range], dtype=np.float64)
number_row = np.arange(1, len(anglesteps_cos) + 1, 1)
zeros = np.zeros(len(number_row), dtype=int)

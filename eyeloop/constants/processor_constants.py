import numpy as np

angular_iter = 24
angular_range = np.arange(angular_iter, dtype=np.int8)
point_source = np.zeros(angular_iter, dtype=np.float64)
step_list_source = np.zeros(angular_iter, dtype=np.int8)

step_size = np.deg2rad(360 / angular_iter)
limit = np.arange(250)  # max size of shape; normalize qqqq
cos_sin_steps = np.array([(np.cos(i * step_size), np.sin(i * step_size)) for i in angular_range], dtype=np.float64)

kernel = np.ones((3, 3), np.uint8)

master_eye = np.eye(200, 200, dtype=bool)
sqrt_two = np.sqrt(2) #diagonal pythagoras


cos_angle_p225 = np.cos(np.radians(22.5))
sin_angle_p225 = np.sin(np.radians(22.5))

cos_angle_p225p90 = np.cos(np.radians(22.5 + 90))
sin_angle_p225p90 = np.sin(np.radians(22.5 + 90))

cos_angle_p225p45 = np.cos(np.radians(22.5 + 45))
sin_angle_p225p45 = np.sin(np.radians(22.5 + 45))

cos_angle_p225m45 = np.cos(np.radians(22.5 - 45))
sin_angle_p225m45 = np.sin(np.radians(22.5 - 45))
rr_stock = np.zeros((16), dtype=int)

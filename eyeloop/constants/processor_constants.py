import numpy as np
import eyeloop.config as config


angular_iter = 24
angular_range = np.arange(angular_iter, dtype=np.int8)
point_source = np.zeros(angular_iter, dtype=np.float64)
step_list_source = np.zeros(angular_iter, dtype=np.int8)

diagonal_size = 2**10

step_size = np.deg2rad(360 / angular_iter)
limit = np.arange(250)  # max size of shape; normalize qqqq
cos_sin_steps = np.array([(np.cos(i * step_size), np.sin(i * step_size)) for i in angular_range], dtype=np.float64)

kernel = np.ones((1, 1), np.uint8)

main_diagonal = np.eye(diagonal_size, diagonal_size, dtype=bool)

#atan(1/2.414) = 22.5 ~atan(1/2) = 26.57 deg

half_diagonal = np.full((diagonal_size, diagonal_size), False, dtype=bool)
fourth_diagonal = half_diagonal.copy()
third_diagonal = half_diagonal.copy()
onefourth = 1/4
onethird = 1/3


invhalf_diagonal = half_diagonal.copy()
invfourth_diagonal = half_diagonal.copy()
invthird_diagonal = half_diagonal.copy()

for i, _ in enumerate(half_diagonal):
    half_diagonal[int(i/2), i] = True
    fourth_diagonal[int(i/4), i] = True
    third_diagonal[int(i/3), i] = True

    invhalf_diagonal[i, int(i/2)] = True
    invfourth_diagonal[i, int(i/4)] = True
    invthird_diagonal[i, int(i/3)] = True


rr_stock = np.zeros((32), dtype=np.float64)

rr_2d = np.zeros((32, 2), dtype=np.float64)
rr_2d_cr = np.zeros((4, 2), dtype=np.float64)

rx_multiply = np.ones((32), dtype=np.float64)
ry_multiply = rx_multiply.copy()

crop_stock = np.zeros((32), dtype=int)
crop_stock_cr = np.zeros((4), dtype=int)
center_shape = (2, 31)


onehalf_ry_add = [8,10,12,14]
onehalf_rx_add = [8,11,12,15]
onehalf_rx_subtract = [9,10,13,14]
onehalf_ry_subtract = [9,11,13,15]
onehalf_ry_multiplier = [8,9,10,11]
onehalf_rx_multiplier = [12,13,14,15]


onefourth_ry_add = [16,19,20,21]
onefourth_rx_add = [16,17,20,23]
onefourth_rx_subtract = [18,19,21,22]
onefourth_ry_subtract = [17,18,22,23]
onefourth_ry_multiplier = [16,17,18,19]
onefourth_rx_multiplier = [20,21,22,23]


onethird_ry_add = [24,25,28,29]
onethird_rx_add = [24,27,28,31]
onethird_rx_subtract = [25,26,29,30]
onethird_ry_subtract = [26,27,30,31]
onethird_ry_multiplier = [24,25,26,27]
onethird_rx_multiplier = [28,29,30,31]


rx_multiplied = np.array(np.concatenate((onehalf_rx_multiplier, onefourth_rx_multiplier, onethird_rx_multiplier)), dtype=int)
ry_multiplied = np.array(np.concatenate((onehalf_ry_multiplier, onefourth_ry_multiplier, onethird_ry_multiplier)), dtype=int)
ones_ = np.ones(4, dtype=np.float64)
rx_multiply = np.array(np.concatenate((ones_ * .5, ones_ * onefourth, ones_*onethird)))

ry_multiply = np.array(np.concatenate((ones_ * .5, ones_ * onefourth, ones_*onethird)))

#rx_multiply[onethird_rx_multiplier] = onethird
#rx_multiply[onefourth_rx_multiplier] = onefourth
#rx_multiply[onehalf_rx_multiplier] = .5

#ry_multiply[onethird_ry_multiplier] = onethird
#ry_multiply[onefourth_ry_multiplier] = onefourth
#ry_multiply[onehalf_ry_multiplier] = .5


ry_add = np.array(np.concatenate(([0, 2, 4],onehalf_ry_add,onefourth_ry_add,onethird_ry_add)),dtype=int)
rx_add = np.array(np.concatenate(([1, 2, 5],onehalf_rx_add,onefourth_rx_add,onethird_rx_add)), dtype=int)


ry_subtract = np.array(np.concatenate(([3, 5, 7],onehalf_ry_subtract,onefourth_ry_subtract,onethird_ry_subtract )))


rx_subtract = np.array(np.concatenate(([3, 4, 6],onehalf_rx_subtract,onefourth_rx_subtract,onethird_rx_subtract)))



black = [35, 35, 35]

angle_dev = -22.5

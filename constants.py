import numpy as np

lower_bands = 2
higher_bands = 5
black_threshhold = 100
a = 2
#action = []

thresh_low_green = np.array([0, 60, 0])
thresh_high_green = np.array([60, 255, 60])

thresh_low_black = (0, 0, 0)
thresh_high_black = (50, 50, 50)
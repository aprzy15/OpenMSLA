#!/usr/bin/env python3

import numpy as np
import time
# Map the screen as Numpy array
# N.B. Numpy stores in format HEIGHT then WIDTH, not WIDTH then HEIGHT!
# c is the number of channels, 4 because BGRA
h, w, c = 3600, 1920, 3
fb = np.memmap('/dev/fb0', dtype='uint8', mode='r+', shape=(h,w,c))

# Fill entire screen with blue - takes 29 ms on Raspi 4
fb[:] = [255,255, 255]

# Fill top half with red - takes 15 ms on Raspi 4
fb[:h//2] = [0,0,255]

# Fill bottom right quarter with green - takes 7 ms on Raspi 4
fb[h//2:, w//2:] = [0,255,0]



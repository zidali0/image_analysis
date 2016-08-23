# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:27:43 2016

@author: zidali
"""

import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import misc 
from imgBase import ImageBase

DAPI = np.array([0, 0, 1])
GFP = np.array([0, 1, 0])
RED = np.array([1, 0, 0])
CYAN = np.array([0, 1, 1])

color_dict = {'c2': DAPI, 'c3': GFP, 'c4': RED, 'c5': CYAN}


class ImageColor(ImageBase):
	dir_name = 'Colored_images'
	pre_image = None
	curr_image = None

	def __init__(self, *args, **kwargs):
		super(ImageColor, self).__init__(*args, **kwargs)
		self.color_images()

	def color_images(self):
		for image_path, image_name in self.images:
                 img = self.get_raw_images(image_path)
                 if 'c1' in image_name:
                     self.save_image(img, image_name)
                     continue
                 m, n = img.shape
                 color = color_dict[image_name.split('.')[0].split('_')[-1]]
                 img_colored = np.zeros((m, n, 3), dtype = np.dtype('uint8'))
                 img_colored[:, :, 0] = img[:, :] * color[0]
                 img_colored[:, :, 1] = img[:, :] * color[1]
                 img_colored[:, :, 2] = img[:, :] * color[2]
                 self.save_image(img_colored, image_name)
      

	def save_image(self, image, image_name):
		print image_name
		misc.imsave(self.output_data_dir +'/' + image_name, image)

if __name__ == '__main__':
	t = ImageColor()


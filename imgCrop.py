import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import misc 
from imgBase import ImageBase

class ImageCrop(ImageBase):
	dir_name = 'cropped_images'
	pre_image = None
	curr_image = None

	def __init__(self, *args, **kwargs):
		super(ImageCrop, self).__init__(*args, **kwargs)
		self.crop_images()

	def crop_images(self):
		for image_path, image_name in self.images:
			self.curr_image = image_name.split('.')[0].split('_')[0]
			raw_image, _, closed_image = self.get_images(image_path)
			if not self.pre_image or self.pre_image != self.curr_image:
				self.get_pattern_centroid(closed_image)
				self.get_pattern_border(closed_image)
			cropped_image = self.get_cropped_image(raw_image)
			self.save_image(cropped_image, image_name)
			self.pre_image = self.curr_image

	def save_image(self, image, image_name):
		print image_name
		misc.imsave(self.output_data_dir +'/' + image_name, image)

if __name__ == '__main__':
	t = ImageCrop()


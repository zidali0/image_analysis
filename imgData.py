import numpy as np
import pandas as pd
from imgBase import ImageBase


class PatternIntensity(ImageBase):
	dir_name = 'data'
	df_mold = None
	curr_df = None
	pre_image = None
	curr_image = None
	channel = None

	def __init__(self, *args, **kwargs):
		super(PatternIntensity, self).__init__(*args, **kwargs)
		self.calculate_intensity()

	def calculate_intensity(self):
		for image_path, image_name in self.images:
			print "Processing image: " + image_name
			self.curr_image, self.channel = image_name.split('.')[0].split('_')
			same_group = False
			if self.df_mold is None:
				self.create_df_mold()
				self.curr_df = self.get_new_df()	
			elif self.pre_image == self.curr_image:
				self.curr_df[self.channel] = 0
				same_group = True
			elif self.pre_image != self.curr_image:
				self.save_data()
				self.curr_df = self.get_new_df()
			self.go_intensity(image_path, same_group)
			self.pre_image = self.curr_image
		self.save_data()

	def go_intensity(self, image_path, same_group):
		if same_group:
			grey_img = self.get_grey_images(image_path)
		else:
			raw_img, grey_img, closed_img = self.get_images(image_path)
			self.get_pattern_centroid(closed_img)
			self.get_pattern_border(closed_img)
		new_img = self.get_cropped_image(grey_img)
		self.get_image_intensity(new_img)

	def get_image_intensity(self, image):
		rows, cols = image.shape
		centerX, centerY = rows/2, cols/2
		for row in xrange(rows):
			for col in xrange(cols):
				index = np.power(row-centerX, 2) + np.power(col-centerY, 2)
				self.curr_df.loc[index][self.channel] += image[row][col]

	def save_data(self):
		file_name = self.pre_image + '.csv'
		self.curr_df = self.curr_df.div(self.curr_df['count'], axis=0)
		self.curr_df.drop('count', axis=1, inplace=True)
		self.curr_df.to_csv(self.data_dir + '/' + file_name)

	def get_new_df(self):
		self.curr_df = self.df_mold.copy(deep=True)
		self.curr_df[self.channel] = 0
		return self.curr_df

	def create_df_mold(self):
		if not self.df_mold:
			pixels = int(self.diameter * self.MICRO_TO_PIXEL)
			center = pixels/2
			distances = {}
			for row in xrange(pixels):
				for col in xrange(pixels):
					index = np.power(row-center, 2) + np.power(col-center, 2)
					distances[index] = distances.get(index, 0) + 1
			items = sorted(distances.items(), key=lambda item:item[0])
			index = [item[0] for item in items]
			counts = [item[1] for item in items]
			self.df_mold = pd.DataFrame(counts, index=index, columns=['count'])
		return self.df_mold

if __name__ == '__main__':
	t = PatternIntensity()



from scipy import misc 
from scipy.ndimage.morphology import binary_closing, binary_fill_holes
from skimage.measure import label, regionprops
from PIL import Image
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import math
import os
import sys

# 0.6212 um/px
DIAMETER = 400
MICRO_TO_PIXEL = 1.6098

offset = int(DIAMETER/2*MICRO_TO_PIXEL)

class PatternIntensity(object):
	DIAMETER = 400
	MICRO_TO_PIXEL = 1.6098
	df_mold = None
	curr_df = None

	data_dir = None
	images = None
	pre_image = None
	curr_image = None
	channel = None

	def __init__(self, image_dir):
		self.img_dir = image_dir
		self.calculate_intensity()

	def calculate_intensity(self):
		self.get_things_ready()
		for image_path, image_name in self.images:
			self.curr_image, self.channel = image_name.split('.')[0].split('_')
			if self.df_mold is None:
				self.create_df_mold()
				self.curr_df = self.get_new_df()	
			elif self.pre_image == self.curr_image:
				self.curr_df[self.channel] = 0
			elif self.pre_image != self.curr_image:
				self.save_data()
				self.curr_df = self.get_new_df()
			self.go_intensity(image_path)
			self.pre_image = self.curr_image
		self.save_data()

	def get_new_df(self):
		self.curr_df = self.df_mold.copy(deep=True)
		self.curr_df[self.channel] = 0

	def save_data(self):
		file_name = self.pre_image + '.csv'
		self.curr_df.div(self.curr_df['count'], axis=0)
		self.curr_df.drop('count', axis=1, inplace=True)
		self.curr_df.to_csv(self.data_dir + '/' + file_name)

	def get_things_ready(self):
		self.offset = int(DIAMETER/2*MICRO_TO_PIXEL)
		self.create_data_dir()
		self.images = self.get_all_images()

	def create_data_dir(self):
		path = self.img_dir + '/data'
		if not self.data_dir:
			try:
				os.makedirs(path)
			except OSError:
				if not os.path.isdir(path):
					print "failed to create data directory"
		return self.data_dir

	def get_all_images(self):
		for root, directories, files in os.walk(self.img_dir):
			for filename in files:
				if filename.endswith(('.JPG', '.jpg', '.TIF', '.tif')):
					filepath = os.path.join(root, filename)
					yield filepath, filename

	def create_df_mold(self):
		if not self.df_mold:
			pixels = int(self.DIAMETER * self.MICRO_TO_PIXEL)
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

	def go_intensity(self, image_path):
		raw_img, grey_img, closed_img = self.get_images(image_path)
		centroid = self.get_pattern_centroid(closed_img)
		top, bottom, left, right = self.get_pattern_border(centroid)
		new_img = self.get_cropped_image(grey_img, top, bottom, left, right)

	def get_images(self, image_name):
		raw_img = misc.imread(image_name)
		grey_img = misc.imread(image_name, flatten=True)
		binary_img = self.get_binary_images(grey_img)
		closed_img = self.get_closed_images(binary_img)
		return raw_img, grey_img, closed_img

	def get_binary_images(self, grey_img):
		return (grey_img > grey_img.mean())*255

	def get_closed_images(self, binary_img):
		return binary_fill_holes(binary_closing(binary_img))

	def get_pattern_centroid(self, closed_img):
		labeled_img = label(closed_img)
		regions = regionprops(labeled_img)
		circle = max(regions, key=lambda item: item.area)
		y, x = circle.centroid
		return np.array([int(x), int(y)])

	def get_pattern_border(self, centroid):
		left, top = centroid - offset
		right, bottom = centroid + offset
		return top, bottom, left, right

	def get_cropped_image(self, raw_img, top, bottom, left, right):
		return raw_img[top:bottom, left:right]

	def get_image_intensity(self, image):
		rows, cols = image.shape
		centerX, centerY = rows/2, cols/2

		for row in xrange(rows):
			for col in xrange(cols):
				index = np.power(row-centerX, 2) + np.power(col-centerY, 2)
				self.curr_df.loc[index][self.channel] += image[row][col]

	def plot_image(self, image):
		plt.figure()
		plt.imshow(image)
		plt.show()

if __name__ == '__main__':
	try:
		img_dir = sys.args[1]
	except Exception:
		img_dir = os.getcwd()
	t = PatternIntensity(img_dir)


	# raw_img, grey_img, closed_img = get_images("test_1.jpg")
	# centroid = get_pattern_centroid(closed_img)
	# top, bottom, left, right = get_pattern_border(centroid)
	# new_img = get_cropped_image(grey_img, top, bottom, left, right)
	# r, c = new_img.shape
	# index = create_df_index(r, c, r/2, c/2)
	# intensity = get_image_intensity(new_img)
	# plot_image(new_img)


# raw_img = misc.imread('test_1.jpg')
# grey = misc.imread('test_1.jpg', flatten=True)
# grey_img = (grey > grey.mean())*255


# # raw_img = Image.open('test_1.jpg')
# # grey_img = raw_img.convert('L')

# close_img = binary_fill_holes(binary_closing(grey_img))
# label_img = label(close_img)

# regions = regionprops(label_img)
# circle = max(regions, key=lambda item: item.area)
# y0, x0 = circle.centroid
# x0 = int(x0)
# y0 = int(y0)

# top = y0 - offset
# bottom = y0 + offset
# left = x0 - offset
# right = x0 + offset

# new_img = raw_img[top:bottom, left:right]



# fig, ax = plt.subplots()

# plt.subplot(231)
# plt.imshow(raw_img)

# plt.subplot(232)
# plt.imshow(grey_img, cmap=plt.cm.gray)

# plt.subplot(233)
# plt.imshow(close_img, cmap=plt.cm.gray)

# plt.subplot(234)
# plt.imshow(label_img, cmap=plt.cm.gray)


# minr, minc, maxr, maxc = circle.bbox
# bx = (minc, maxc, maxc, minc, minc)
# by = (minr, minr, maxr, maxr, minr)
# plt.plot(bx, by, '-b', linewidth=2.5)
# plt.plot(x0, y0, '.r', markersize=15)

# plt.subplot(235)
# plt.imshow(new_img)
# plt.show()

# plt.show()



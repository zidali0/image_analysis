import matplotlib
matplotlib.use("TkAgg")
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
import Tkinter as tk
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog


class PatternIntensity(object):
	MICRO_TO_PIXEL = 1.6098
	diameter = 400

	df_mold = None
	curr_df = None
	data_dir = None
	images = None
	pre_image = None
	curr_image = None
	channel = None

	def __init__(self, image_dir):
		self.get_input_information()
		self.get_things_ready()
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

	def get_things_ready(self):
		self.offset = int(self.diameter/2*self.MICRO_TO_PIXEL)
		self.create_data_dir()
		self.images = self.get_all_images()

	def create_data_dir(self):
		path = self.image_dir + '/data'
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except OSError:
				if not os.path.isdir(path):
					print "failed to create data directory"
		else:
			self.data_dir = path
		return self.data_dir

	def get_all_images(self):
		for root, directories, files in os.walk(self.image_dir):
			for filename in files:
				if filename.endswith(('.JPG', '.jpg', '.TIF', '.tif')):
					filepath = os.path.join(root, filename)
					yield filepath, filename

	def go_intensity(self, image_path, same_group):
		if same_group:
			grey_img = self.get_grey_images(image_path)
		else:
			raw_img, grey_img, closed_img = self.get_images(image_path)
			self.get_pattern_centroid(closed_img)
			self.get_pattern_border()
		new_img = self.get_cropped_image(grey_img)
		self.get_image_intensity(new_img)

	def get_images(self, image_name):
		raw_img = misc.imread(image_name)
		grey_img = self.get_grey_images(image_name)
		binary_img = self.get_binary_images(grey_img)
		closed_img = self.get_closed_images(binary_img)
		return raw_img, grey_img, closed_img

	def get_grey_images(self, image_name):
		return misc.imread(image_name, flatten=True)

	def get_binary_images(self, grey_img):
		return (grey_img > grey_img.mean())*255

	def get_closed_images(self, binary_img):
		return binary_fill_holes(binary_closing(binary_img))

	def get_pattern_centroid(self, closed_img):
		labeled_img = label(closed_img)
		regions = regionprops(labeled_img)
		circle = max(regions, key=lambda item: item.area)
		y, x = circle.centroid
		self.centroid = np.array([int(x), int(y)])
		return self.centroid

	def get_pattern_border(self):
		self.left, self.top = self.centroid - self.offset
		self.right, self.bottom = self.centroid + self.offset
		return self.top, self.bottom, self.left, self.right

	def get_cropped_image(self, grey_img):
		return grey_img[self.top:self.bottom, self.left:self.right]

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

	def plot_image(self, image):
		plt.figure()
		plt.imshow(image)
		plt.show()

	def get_input_information(self):
		root = tk.Tk()
		root.title("Please specify image directory and pattern diameter")
		root.geometry("600x100")
		frame = tk.Frame(root)
		frame.pack()

		dir_label = tk.Label(frame, text="Image Directory: ")
		dir_label.grid(row=0, column=1, sticky=W)
		diameter_label = tk.Label(frame, text="Pattern Diameter (um): ")
		diameter_label.grid(row=1, column=1, sticky=W)
	
		dir_var = tk.StringVar()
		self.dir_entry = tk.Entry(frame, textvariable=dir_var)
		self.dir_entry.config(width=40)
		self.dir_entry.grid(row=0, column=2)

		diameter_var = tk.IntVar()
		diameter_var.set(400)
		self.diameter_entry = tk.Entry(frame, textvariable=diameter_var)
		self.diameter_entry.config(justify='left')
		self.diameter_entry.grid(row=1, column=2, sticky=W)

		dir_btn = tk.Button(frame, text = 'Open', command = self.fetch_entry)
		dir_btn.config(background='blue')
		dir_btn.grid(row = 0, column = 3)

		submit_btn = tk.Button(frame, text = 'Submit', command = root.destroy)
		submit_btn.grid(row = 3, column=3)

		root.mainloop()

		self.image_dir = dir_var.get() 
		self.diameter = int(diameter_var.get())

	def fetch_entry(self):
		self.dir_entry.delete(0)
		self.dir_entry.insert(0, tkFileDialog.askdirectory())

if __name__ == '__main__':
	try:
		image_dir = sys.args[1]
	except Exception:
		image_dir = os.getcwd()
	t = PatternIntensity(image_dir)



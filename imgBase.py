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

class ImageBase(object):

	MICRO_TO_PIXEL = 1.6098
	MICRO_TO_PIXEL = 1.6098*2
	diameter = 400

	output_data_dir = None
	dir_name = None
	images = None

	def __init__(self):
		self.get_input_information()
		self.get_things_ready()

	def get_things_ready(self):
		self.offset = int(self.diameter/2*self.MICRO_TO_PIXEL)
		self.create_output_data_dir()
		self.images = self.get_all_images()

	def create_output_data_dir(self):
		path = self.image_dir + '/' + self.dir_name
		if not os.path.exists(path):
			try:
				os.makedirs(path)
			except OSError:
				if not os.path.isdir(path):
					print "failed to create data directory"
		self.output_data_dir = path
		return self.output_data_dir

	def get_all_images(self):
		for root, directories, files in os.walk(self.image_dir):
			for filename in files:
				if filename.endswith(('.JPG', '.jpg', '.TIF', '.tif')):
					filepath = os.path.join(root, filename)
					yield filepath, filename

	def get_images(self, image_name):
		raw_img = self.get_raw_images(image_name)
		gray_img = self.get_gray_images(image_name)
		binary_img = self.get_binary_images(gray_img)
		closed_img = self.get_closed_images(binary_img)
		return raw_img, gray_img, closed_img

	def get_raw_images(self, image_name):
		return misc.imread(image_name)

	def get_gray_images(self, image_name):
		return misc.imread(image_name, flatten=True)

	def get_binary_images(self, gray_img):
		return (gray_img > gray_img.mean())*255

	def get_closed_images(self, binary_img):
		return binary_fill_holes(binary_closing(binary_img))

	def get_pattern_centroid(self, closed_img):
		labeled_img = label(closed_img)
		regions = regionprops(labeled_img)
		circle = max(regions, key=lambda item: item.area)
		y, x = circle.centroid
		self.centroid = np.array([int(x), int(y)])
		return self.centroid

	def get_pattern_border(self, closed_img):
		self.left, self.top = self.centroid - self.offset
		self.right, self.bottom = self.centroid + self.offset
		self.left, self.top = max(self.left, 0), max(self.top, 0)
		self.right, self.bottom = min(self.right, closed_img.shape[1]), min(self.bottom, closed_img.shape[0])
		return self.top, self.bottom, self.left, self.right

	def get_cropped_image(self, gray_img):
		return gray_img[self.top:self.bottom, self.left:self.right]

	def get_input_information(self):
		root = tk.Tk()
		root.title("Please specify image/data directory and pattern diameter")
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
		self.dir_entry.insert(0, tkFileDialog.askdirectory(initial=os.getcwd()))

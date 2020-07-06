#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rospkg

from random import randint
from datetime import datetime

pkg_name = 'motivational_model'
rospack = rospkg.RosPack()

class Logger():
	"""
	Logger Class
	"""
	def __init__(self, folder, subfolder=None):
		"""
		Creates log files named as classes
		@ class_name str: class name
		"""
		# If a subfolder is not specified it is created with the current time as name
		if subfolder is None:
			self.__path = rospack.get_path(pkg_name) + '/data/' + folder + '/' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		else:		
			self.__path = rospack.get_path(pkg_name) + '/data/' + folder + "/" + subfolder + '/' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		if not os.path.isdir(self.__path):
			os.makedirs(self.__path)

	def write_file(self, key, value):
		"""
		Writes data into a file
		@ key str: variable name
		@ value float: variable value
		"""
		# Opens the file in write mode in the specified path
		text_file=open(self.__path+"/"+str(key)+".txt","a")
		text_file.write(str(datetime.now())+";"+unicode(str(value))+'\n')
		text_file.close()
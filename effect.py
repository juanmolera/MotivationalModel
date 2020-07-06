#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Effect():
	"""
	Action Effect Class
	"""
	def __init__(self, id, constancy, params_std):

		self.__id = id
		self.__constancy = constancy
		self.__params_std = params_std

		self.__related_hv = list() # Stores Homeostatic Variable objects related to Effect

	def get_id(self):
		"""
		Returns Effect id
		"""
		return self.__id

	def get_constancy(self):
		"""
		Returns Effect constancy. 2 possibilities.
		@ 0 = Continuous: action is continuous over a period of time
		@ 1 = Punctual: action is discrete
		"""
		return self.__constancy

	def add_hv(self, var):
		"""
		Adds Homeostatic Variable objects to the list
		@ var object: Homeostatic Variable object
		"""
		self.__related_hv.append(var)

	def get_params_std(self):
		"""
		Returns Standard Evolution Parameters related to Effect object
		"""
		return self.__params_std

	def get_related_hv(self):
		"""
		Returns Related Homeostatic Variable objects list
		"""
		return self.__related_hv


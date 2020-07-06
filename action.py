#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Action():
	"""
	Action Class
	"""
	def __init__(self, id, name, type, related_ag):

		self.__name = name
		self.__id = id
		self.__type = type
		self.__related_ag = related_ag
		
		self.__effects = list() # Stores related Effects
		
	def get_id(self):
		"""
		Returns Action id
		"""
		return self.__id

	def get_name(self):
		"""
		Returns Action name
		"""
		return self.__name

	def get_type(self):
		"""
		Returns Action type. 2 possibilities.
		@ 0 = Endogenous: action is executed by the system
		@ 1 = Exogenous: action is executed by an external agent
		"""
		return self.__type

	def get_constancy(self):
		"""
		Returns Action constancy. 2 possibilities.
		@ 0 = Continuous: action is continuous over a period of time
		@ 1 = Punctual: action is discrete
		"""
		return self.__constancy

	def add_eff(self, var):
		"""
		Adds Effect object to the list
		@ var Effect: Action Effect object
		"""
		self.__effects.append(var)

	def get_effects(self):
		"""
		Returns Effect objects list
		"""
		return self.__effects

	def get_related_ag(self):
		"""
		Returns Related Agent Name
		"""
		return self.__related_ag
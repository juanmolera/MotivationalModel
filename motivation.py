#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motivational_model.classes.homeostaticvariable import HomeostaticVariable
from motivational_model.classes.stimulus import Stimulus
from motivational_model.classes.agent import Agent
from motivational_model.logger.log import Logger

ALPHA = 0.01

class Motivation(Logger):
	"""
	Motivation Class
	"""
	def __init__(self, id, name, threshold, logging=False):

		self.__id = id
		self.__name = name
		self.__threshold = threshold

		self.__related_hv = list() # Stores related Homeostatic Variables
		self.__related_sti = list() # Stores related Stimuli
		self.__related_ag = list() # Stores related Agents

		self.__value = 0

		# Logger
		self.__logging = logging
		Logger.__init__(self, "Experiment", "Motivations") # Creates Log file

	def get_id(self):
		"""
		Returns Motivation id
		"""	
		return self.__id

	def get_name(self):
		"""
		Returns Motivation name
		"""
		return self.__name

	def get_threshold(self):
		"""
		Returns Motivation threslhold value
		"""
		return self.__threshold
	
	def add_hv(self, var):
		"""
		Adds Homeostatic Variable objects to the list
		@ var HomeostaticVariable: Homeostatic Variable object
		"""
		self.__related_hv.append(var)
		
	def add_sti(self, var):
		"""
		Adds Stimulus objects to the list
		@ var Stimulus: Stimulus object
		"""
		self.__related_sti.append(var)

	def add_ag(self, var):
		"""
		Adds Agent objects to the list
		@ var Agent: Agent object
		"""
		self.__related_ag.append(var)
	
	def get_value(self):
		"""
		Returns Motivation Deficit value
		"""
		hv_sum = 0
		sti_sum = 0
		ag_sum = 0

		hv_value = 0
		es_value = 0
		value = 0

		for hv in self.__related_hv:
			hv_sum += hv.get_hv_value()

		for sti in self.__related_sti:
			for state in sti.get_states():
				sti_sum += state.get_value()
		
		for ag in self.__related_ag:
			for state in ag.get_states():
				ag_sum += state.get_value()

		if bool(self.__related_hv):
			hv_value = 1/float(len(self.__related_hv)) * hv_sum

		if bool(self.__related_ag):
			es_value += 1.0/len(self.__related_ag) * ag_sum 
		if bool(self.__related_sti):
			es_value += 1.0/len(self.__related_sti) * sti_sum

		value = hv_value + ALPHA*hv_value*es_value

		if self.__logging and value != self.__value:

			Logger.write_file(self, self.__name, self.__value) # Writes Motivation name and value

		return value
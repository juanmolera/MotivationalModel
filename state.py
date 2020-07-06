#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motivational_model.classes.temporalevolution import TemporalEvolution
from motivational_model.logger.log import Logger

class State(Logger):
	"""
	State Class
	"""
	def __init__(self, id, name, related_ag, related_sti, params_act, params_deact, time_step=1.0, logging=False):

		self.__id = id
		self.__name = name
		self.__value = -1

		# Evolution Parameters
		self.__params_act = params_act
		self.__params_deact = params_deact

		# Related agent or stimuli
		self.__related_ag = related_ag
		self.__related_sti = related_sti

		# Logger
		self.__logging = logging
		Logger.__init__(self, "Experiment", "States") # Creates Log file

		# Creates Agent/Stimulus Temporal Evolution objects
		self.__activation = TemporalEvolution(id, name +"_activation", 0, 100, 100, 0, 0, params_act, False, time_step)
		self.__activation.start() # Starts the thread

		self.__deactivation = TemporalEvolution(id, name +"_deactivation", 0, 100, 100, 0, 0, params_deact, False, time_step)
		self.__deactivation.start() # Starts the thread

	def get_id(self):
		"""
		Returns State id
		"""
		return self.__id

	def get_name(self):
		"""
		Returns State name
		"""
		return self.__name

	def get_related_ag(self):
		"""
		Returns Related Agent
		"""
		return self.__related_ag

	def get_related_sti(self):
		"""
		Returns Related Stimuli
		"""
		return self.__related_sti

	def get_params_act(self):
		"""
		Returns Activation Parameters
		"""
		return self.__params_std

	def get_params_deact(self):
		"""
		Returns Deactivation Parameters
		"""
		return self.__params_destd

	def get_activation(self):
		"""
		Returns State Activation object
		"""
		return self.__activation

	def get_deactivation(self):
		"""
		Returns State Deactivation object
		"""
		return self.__deactivation

	def set_state_evolution(self, active):
		"""
		Sets Evolving Value for State Evolutions
		"""
		if active:
			self.__activation.set_value(self.__deactivation.get_value())
			self.__activation.set_evolving_value(True)
			self.__deactivation.set_evolving_value(False)
		else:
			self.__deactivation.set_value(self.__activation.get_value())
			self.__activation.set_evolving_value(False)
			self.__deactivation.set_evolving_value(True)

	def get_value(self):
		"""
		Returns External Stimuli Deficit value
		"""
		value = 0

		if self.__activation.is_evolving():
			value = self.__activation.get_value()
		else:
			value = self.__deactivation.get_value()
			
		if value > 100:
			value = 100			
		elif value < 0:
			value = 0

		if self.__logging and value != self.__value:

			Logger.write_file(self, self.__name, value) # Writes State name and value
			
		return value
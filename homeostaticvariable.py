#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motivational_model.classes.temporalevolution import TemporalEvolution
from motivational_model.classes.effect import Effect
from motivational_model.logger.log import Logger

class HomeostaticVariable(TemporalEvolution, Logger):
	"""
	Homeostatic Variable Class
	"""
	def __init__(self, id, name, initial_value, ideal_value, upper_limit, lower_limit, satisfaction_time, params_std, time_step=1.0, logging=False):
		
		self.__id = id
		self.__name = name

		# Evolution Parameters
		self.__initial_value = initial_value
		self.__ideal_value = ideal_value
		self.__upper_limit = upper_limit
		self.__lower_limit = lower_limit
		self.__satisfaction_time = satisfaction_time
		self.__params_std = params_std

		self.__time_step = time_step

		self.__eff_evols = list() # Stores Effect Temporal Evolution objects

		self.__value = 0 # Initializes Homeostatic Variable Value

		# Creates Homeostatic Variable Temporal Evolution object
		self.__hv_evol = TemporalEvolution(id, name, initial_value, ideal_value, upper_limit, lower_limit, satisfaction_time, params_std, True, time_step)
		self.__hv_evol.start() # Starts the thread

		# Logger
		self.__logging = logging
		Logger.__init__(self, "Experiment", "HomeostaticVariables") # Creates Log file

	def get_id(self):
		"""
		Returns Homeostatic Variable id
		"""
		return self.__id
		
	def get_name(self):
		"""
		Returns Homeostatic Variable name
		"""
		return self.__name

	def get_hv_evol(self):
		"""
		Returns Homeostatic Variable Temporal Evolution object
		"""
		return self.__hv_evol

	def get_initial_value(self):
		"""
		Returns Homeostatic Variable initial value
		"""
		return self.__initial_value

	def get_ideal_value(self):
		"""
		Returns Homeostatic Variable ideal value
		"""
		return self.__ideal_value

	def get_upper_limit(self):
		"""
		Returns Homeostatic Variable upper limit
		"""
		return self.__upper_limit

	def get_lower_limit(self):
		"""
		Returns Homeostatic Variable lower limit
		"""
		return self.__lower_limit

	def get_satisfaction_time(self):
		"""
		Returns Homeostatic Variable satisfaction time
		"""
		return self.__satisfaction_time

	def get_params_std(self):
		"""
		Returns Standard Evolution Parameters related to Homeostatic Variable object
		"""
		return self.__params_std

	def get_eff_evols(self):
		"""
		Returns Related Action Effect Temporal Evolution objects list
		"""
		return self.__eff_evols

	def stop(self):
		"""
		Stops evolution
		"""
		return self.__hv_evol.stop()

	def set_value(self, value):
		"""
		Sets new value
		@ value float: value to be set
		"""
		self.__value = value

	def add_effect(self, var):
		"""
		Adds Related Action Effect Temporal Evolution objects to list
		@ var Effect: Effect object
		"""
		if bool(self.__eff_evols):
			for evol in self.__eff_evols:
				if var.get_id() == evol.get_id(): # Avoids repetition
					evol.set_evolving_value(True)
					evol.set_value(self.__hv_evol.get_value())

		# Creates effect and starts if it is not in list
		if not bool(self.__eff_evols) or not var.get_id() in [e.get_id() for e in self.__eff_evols]:
			self.__eff_evols.append(TemporalEvolution(var.get_id(), "effect"+str(var.get_id()), self.__hv_evol.get_value(), self.__ideal_value, self.__upper_limit, self.__lower_limit, self.__satisfaction_time, var.get_params_std(), True, self.__time_step))
			self.__eff_evols[-1].start() # Starts the thread

		# Checks if any effect is running
		if any([e.is_evolving() for e in self.__eff_evols]):
			# Stops current evolution of the hv
			self.__hv_evol.set_evolving_value(False)

	def remove_effect(self, eff_id):
		"""
		Removes Action Effects already taken into account
		@ eff_ids int: Action Effect id
		"""
		if bool(self.__eff_evols):
			for idx, evol in enumerate(self.__eff_evols):
				if evol.get_id() == eff_id:	
					evol.set_evolving_value(False)

		# Checks if any effect is running
		if not any([e.is_evolving() for e in self.__eff_evols]):
			# Gets effect value to be set in hv evolving value
			value = evol.get_value()
			self.__hv_evol.set_value(value)
			self.__hv_evol.set_evolving_value(True)

	def get_hv_value(self):
		"""
		Returns Homeostatic Variable Deficit value
		"""
		aux_value = 0
		value = None

		if bool(self.__eff_evols) and any([e.is_evolving() for e in self.__eff_evols]):

			for evol in self.__eff_evols:
				if evol.is_evolving():
					aux_value += evol.get_value()

			value = aux_value

			if value > self.__upper_limit:
				value = self.__upper_limit
				
			elif value < self.__lower_limit:
				value = self.__lower_limit

			for evol in self.__eff_evols:
				evol.set_value(value) # Sets new initial value for multiple Effects
			
			value = self.__ideal_value - value
		
		if value is None:
			value = self.__hv_evol.get_deficit()

		if self.__logging and self.__value != value:

			Logger.write_file(self, self.__name, value) # Writes Homeostatic Variable name and value

		return value
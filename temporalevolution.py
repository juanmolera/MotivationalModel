#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rospy import Publisher, loginfo, logwarn, logerr, sleep
from math import exp, log
from std_msgs.msg import Float32
from threading import Thread, Lock

class TemporalEvolution(Thread):
	"""
	Temporal Evolution Class
	"""
	def __init__(self, id, name, initial_value, ideal_value, upper_limit, lower_limit, satisfaction_time, params_std, evolving, time_step=1.0):
		
		self.__name = name
		self.__id = id

		# Evolution Parameters
		self.__initial_value = initial_value
		self.__current_value = initial_value
		self.__ideal_value = ideal_value
		self.__upper_limit = upper_limit
		self.__lower_limit = lower_limit
		self.__satisfaction_time = satisfaction_time
		self.__params_std = params_std
		self.__time_step = time_step

		# Initializes Evolution
		self.__evolving = evolving
		self.__evol_params = params_std
		self.__punctual = False
		self.__stop = False
		self.__no_saturation = 0.1 # Prevents saturation 

		# Publisher
		self.__pub = Publisher(name.lower() + "/value", Float32, latch=True, queue_size=1)

		# Defines evolving method
		self.__std_evol = self.set_evolution(params_std["te_id"])

		# Creates thread and lock
		Thread.__init__(self, target=self.__std_evol)
		self.__lock = Lock()

	def stop(self):
		"""
		Stops temporal evolution method
		"""
		# Sets evolving to false
		self.set_evolving_value(False)
		# Sets stop to true
		self.__stop = True
		#Thread.__stop()
		Thread.join(self)

	def get_id(self):
		"""
		Gets evolving variable id
		"""
		return self.__id
		
	def set_evolving_value(self, evolving_value):
		"""
		Sets Temporal Evolution evolving value
		"""
		# Locks the resource
		self.__lock.acquire()
		self.__evolving = evolving_value
		# Releases the resource
		self.__lock.release()

	def is_evolving(self):
		"""
		Returns True if the variable is evolving
		"""
		# Locks the resource
		self.__lock.acquire()
		aux =  self.__evolving
		# Releases the resource
		self.__lock.release()

		return aux

	def set_value(self, current_value):
		"""
		Sets current value
		@ current_value float: value to be set
		"""
		# Locks the resource
		self.__lock.acquire()
		self.__current_value = current_value
		# Releases the resource
		self.__lock.release()

	def get_value(self):
		"""
		Returns current Value
		"""
		# Locks the resource
		self.__lock.acquire()
		value = self.__current_value
		# Releases the resource
		self.__lock.release()

		return value

	def set_fn_time(self, actual_value):
		"""
		Sets time value for the exponential and logarithmic functions
		""" 
		self.__fn_time = actual_value

	def get_fn_time(self):
		"""
		Returns time value for the exponential and logarithmic functions
		"""
		return self.__fn_time

	def get_deficit(self):
		"""
		Returns Deficit Value of the evolution
		"""
		# Locks the resource
		self.__lock.acquire()
		value = self.__ideal_value - self.__actual_value
		# Releases the resource
		self.__lock.release()

		return value

	def is_punctual(self):
		"""
		Returns True if the Effect is Punctual
		"""
		return self.__punctual

	def set_evolution(self, te_id):
		"""
		Sets the evolution method for the object
		@ te_id int: evolution id
		"""
		if te_id == 0:
			return self.constant_evolution
		elif te_id == 1:
			return self.linear_evolution
		elif te_id == 2:
			return self.exp_evolution
		elif te_id == 3:
			return self.log_evolution
		elif te_id == 4:
			return self.step_evolution
		else:
			logerr("Params given are not correct")

	def constant_evolution(self):
		"""
		Variable evolves as a constant function
		"""
		self.set_value(self.__actual_value)
		new_value = self.get_value()

		while self.is_evolving() or not self.__stop:
			if self.is_evolving():
				new_value = self.get_value()

				if new_value > self.__upper_limit:
					new_value = self.__upper_limit

				elif new_value < self.__lower_limit:
					new_value = self.__lower_limit

				self.set_value(new_value)
				sleep(self.__time_step)
			else:
				sleep(self.__no_saturation)

	def linear_evolution(self):
		"""
		Variable evolves as a linear function
		"""
		self.set_value(self.__actual_value)

		while self.is_evolving() or not self.__stop:
			new_value = self.get_value()
			if self.is_evolving():
				new_value += self.__evol_params["slope"]
				if new_value > self.__upper_limit:
					new_value = self.__upper_limit
					self.set_value(new_value)
					sleep(self.__satisfaction_time)

				elif new_value < self.__lower_limit:
					new_value = self.__lower_limit

				self.set_value(new_value)
				sleep(self.__time_step)
			else:
				sleep(self.__no_saturation)
	
	def exp_evolution(self):
		"""
		Variable evolves as an exponential function
		"""
		new_value = self.get_value()
		self.set_fn_time(self.__actual_value)
		fntime = self.get_fn_time()

		while self.is_evolving() or not self.__stop:
			if self.is_evolving():
				fntime += 1
				new_value = exp(fntime/self.__evol_params["tau"])
				
				if new_value > self.__upper_limit:
					new_value = self.__upper_limit
					sleep(self.__satisfaction_time)

				elif new_value < self.__lower_limit:
					new_value = self.__lower_limit

				self.set_value(new_value)
				sleep(self.__time_step)
			else:
				sleep(self.__no_saturation)

	def log_evolution(self):
		"""
		Variable evolves as a logarithmic function
		"""
		new_value = self.get_value()
		self.set_fn_time(self.__actual_value)
		fntime = self.get_fn_time()

		while self.is_evolving() or not self.__stop:
			if self.is_evolving():
				fntime += 1
				new_value = log(fntime)
				
				if new_value > self.__upper_limit:
					new_value = self.__upper_limit
					sleep(self.__satisfaction_time)

				elif new_value < self.__lower_limit:
					new_value = self.__lower_limit

				self.set_value(new_value)
				sleep(self.__time_step)
			else:
				sleep(self.__no_saturation)

	def step_evolution(self):
		"""
		Variable evolves as a step function
		"""
		self.__punctual = True
		self.set_value(self.__actual_value)
		new_value = self.get_value()

		while self.is_evolving() or not self.__stop:
			if self.is_evolving():
				new_value += self.__evol_params["step"]
				
				if new_value > self.__upper_limit:
					new_value = self.__upper_limit
					sleep(self.__satisfaction_time)

				elif new_value < self.__lower_limit:
					new_value = self.__lower_limit

				self.set_value(new_value)
				sleep(self.__time_step)
				self.set_evolving_value(False)
			else:
				sleep(self.__no_saturation)

	def __set_time_step(self, time):
		"""
		Sets TIME STEP value
		"""
		self.__time_step = time
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rospy import Subscriber
from handlers.functions import my_import

class Stimulus():
	"""
	Stimulus Class
	"""
	def __init__(self, id, name, current_state, topic, msg, pkg, states):

		self.__id = id
		self.__name = name

		self.__current_state = current_state
		
		if bool(topic) and bool(msg) and bool(pkg):
			self.__topic = topic
			self.__msg = my_import(pkg+".msg", msg)
			self.__pkg = pkg

			# Subscriber
			self.__subs = Subscriber(self.__topic, self.__msg, self.__perception_cb)

		self.__states = states # Stores related States

		# Activates current state
		if bool(self.__current_state):
			self.__current_state.set_state_evolution(True)

	def get_id(self):
		"""
		Returns Stimulus id
		"""
		return self.__id	

	def get_name(self):
		"""
		Returns Stimulus name
		"""
		return self.__name

	def set_stimulus_state(self, state):
		"""
		Sets current State
		@ state State: current state
		"""
		for sta in self.__states:
			if sta.get_name() == state:
				self.__current_state = sta
				self.__current_state.set_state_evolution(True)
			else:
				sta.set_state_evolution(False)

	def get_current_state(self):
		"""
		Returns Stimulus current State object
		"""
		return self.__current_state

	def get_states(self):
		"""
		Returns State list
		"""
		return self.__states

	def add_sta(self, var):
		"""
		Adds State objects to the list
		@ var State: State object
		"""
		self.__states.append(var)

	def __perception_cb(self, msg):
		"""
		Callback Method receives Stimulus information
		"""
		if msg.header.frame_id == self.__name:
			values = {pair.key: pair.value for pair in msg.values}
			
			if "state" in values.keys(): # Gets State
				self.set_stimulus_state(values["state"])
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import itertools 
from datetime import datetime
from copy import copy
from motivational_model.db_loader.loader import DbLoader
from motivational_model.db_loader.relateobject import RelateObject
from motivational_model.classes.motivation import Motivation
from motivational_model.classes.homeostaticvariable import HomeostaticVariable
from motivational_model.classes.stimulus import Stimulus
from motivational_model.classes.action import Action
from motivational_model.classes.agent import Agent
from motivational_model.classes.effect import Effect
from motivational_model.classes.state import State
from motivational_model.logger.log import Logger
from motivational_model.msg import Motivations
from proactive_decision_making.msg import ManagerFeedback
from common_msgs.msg import KeyValuePair
from std_msgs.msg import String

pkg_name = 'motivational_model'

class MotivationalModel(DbLoader, RelateObject, Logger):
    """
    Manager Class
    """
    def __init__(self):
        """
        Init method
        """
        rospy.loginfo("Initializing Motivational Model...")

        # TIMESTEP used as an active pause
        self.TIMESTEP = 1.0
        # Init database
        DbLoader.__init__(self)
        # Init logger
        Logger.__init__(self, "Experiment", "Manager")

        # Data obtained from database by loader
        te = DbLoader.get_data(self, "Temporal_Evolutions") # Temporal Evolution data list read by loader
        std = DbLoader.get_data(self, "Standard_Evolution") # Standard Evolution Parameters data list read by loader
        end_exo = DbLoader.get_data(self, "Endogenous_Exogenous") # Action Endogenous/Exogenous type read by loader
        con = DbLoader.get_data(self, "Constancy") # Action Constancy read by loader
        hv = DbLoader.get_data(self, "Homeostatic_Variables") # Homeostatic Variables data list read by loader
        mot = DbLoader.get_data(self, "Motivations") # Motivations data list read by loader
        sti = DbLoader.get_data(self, "Stimuli") # Stimuli data list read by loader
        act = DbLoader.get_data(self, "Actions") # Actions data list read by loader
        ag = DbLoader.get_data(self, "Agents") # Agents data list read by loader
        sta = DbLoader.get_data(self, "State") # States data list read by loader
        eff = DbLoader.get_data(self, "Actions_Effect") # Actions effect data list read by loader

        # Object lists
        self.__homeostatic_variables = RelateObject().create_hv_list(hv, std, self.TIMESTEP, True) # Homeostatic Variable Object list
        self.__states = RelateObject().create_sta_list(sta, std, self.TIMESTEP, True) # State Object list
        self.__effects = RelateObject().create_eff_list(eff, self.__homeostatic_variables, std, con) # Action Effect Object list
        self.__actions = RelateObject().create_act_list(act, end_exo, self.__effects, ag) # Action Object list
        self.__agents = RelateObject().create_ag_list(ag, self.__states, self.__actions, self.__homeostatic_variables) # Agent Object list
        self.__stimuli = RelateObject().create_sti_list(sti, self.__states) # Stimulus Object list
        self.__motivations = RelateObject().create_mot_list(mot, self.__homeostatic_variables, self.__stimuli, self.__agents, True) # Motivation Object list
        
        self.__active_actions_ids = list() # Current Active Actions
        
        self.__motivational_intensities = list() # Motivations intensities

        # Initializes Dominant Motivation
        self.__current_dom_mot = None
        self.__previous_dom_mot = None
        self.__saved_previous_dom_mot = None

        # Initializes ROS publishers and subscribers
        self.create_msg_srv()

    def create_msg_srv(self):
        """
        This function has to be implemented in the children.
        """
        self.__subs = rospy.Subscriber("decision_making/manager/feedback", ManagerFeedback, self.__callback)

        # Dominant Motivation Publisher
        self.__pub_mot = rospy.Publisher("motivational_model/motivations", Motivations, latch=True, queue_size=1)

    def run(self):
        """
        Main loop.
        """
        # While node is active
        while not rospy.is_shutdown():

            self.__execute()
            rospy.sleep(self.TIMESTEP)

    def stop(self):
        """
        Closes active pubs and subs
        Deletes remaining variables
        Destructor of timers
        """
        rospy.loginfo("Stopping motivational manager and closing threads...")

        # Stops all threads running simultaneously
        for hv in self.__homeostatic_variables:
            # Stops main evolution
            hv.get_evol().stop()
            # Stops effects
            for ef in hv.get_effects():
                ef.stop()

        for a in self.__agents:
            for s in a.get_states():
                s.get_activation().stop()
                s.get_deactivation().stop()

        for es in self.__stimuli:
            for s in es.get_states():
                s.get_activation().stop()
                s.get_deactivation().stop()

        rospy.loginfo("Every Thread closed successfully.")
 
    def __callback(self, msg):
        """
        Callback Method receives Action information
        @ msg ManagerFeedback: actions status
        Creates a list with Current Active Action IDs
        """
        if bool(msg.action) and msg.app_status in [ManagerFeedback().STARTED,ManagerFeedback().STOPPED]:
            for agent in self.__agents:
                for action in agent.get_actions():
                    if action.get_name() == msg.action:
                        if msg.app_status in [ManagerFeedback().STARTED]:
                            if action.get_id() not in self.__active_actions_ids:
                                # Creates effects
                                for effect in action.get_effects():
                                    for hv in self.__homeostatic_variables:
                                        if hv.get_id() in effect.get_related_hv():
                                            hv.add_effect(effect)
                                # Saves action
                                self.__active_actions_ids.append(action.get_id())

                        elif msg.app_status in [ManagerFeedback().STOPPED, ManagerFeedback().CANCELLED, ManagerFeedback().PAUSED, ManagerFeedback().COMPLETED]:
                            if action.get_id() in self.__active_actions:
                                # Removes effects
                                for effect in action.get_effects():
                                    for hv in self.__homeostatic_variables:
                                        if hv.get_id() in effect.get_related_hv():
                                            hv.remove_effect(effect.get_id())
                                self.__active_actions.remove(action.get_id())

    def __execute(self):
        """
        Replaces evolution parameters due to action presence
        """
        # Gets current dominant motivation 
        self.__current_dom_mot, self.__motivational_intensities = self.__get_mot_dominant(copy(self.__current_dom_mot), self.__motivations)

        # Checks if the dominant motivation has changed
        if self.__previous_dom_mot is None:
            self.__previous_dom_mot = self.__current_dom_mot
            self.__saved_previous_dom_mot = self.__current_dom_mot
        else:
            if self.__current_dom_mot.get_id() != self.__previous_dom_mot.get_id():
                # The dominant motivation has changed
                self.__saved_previous_dom_mot = self.__previous_dom_mot
                self.__previous_dom_mot = self.__current_dom_mot 

        # Publishes info every timestep
        self.__pub_mot.publish(dominant=self.__current_dom_mot.get_name(), intensities=self.__motivational_intensities)

    def __get_mot_dominant(self, current_dom_mot, motivations):
        """
        @ current_dom_mot Motivation: copy of the actual dominant motivation
        @ motivations list: list of all motivations
        @ returns current_dom_mot Motivation: dominant motivation
        @ returns intensities list: motivational intensities list
        """
        intensities = list()
        aux_mot = None

        if current_dom_mot is None:
            max_value = 0
        else:
            max_value = current_dom_mot.get_value()
            current_dom_mot = None

       for mot in motivations:
            if mot.get_value() >= mot.get_threshold():
                if mot.get_value() > max_value or (mot.get_name() == self.__current_dom_mot.get_name() and mot.get_value() >= max_value):
                    current_dom_mot = copy(mot)
                    max_value = mot.get_value()
            if mot.get_name() == "none":
                aux_mot = mot
            mot.save()
            
            # Get motivational intensities
            intensities.append(KeyValuePair(key=mot.get_name(), value=str(mot.get_value())))
            # Log info message
            rospy.loginfo("\tValue of %s is %.2f", mot.get_name(), mot.get_value())

        if current_dom_mot is None:
            current_dom_mot = copy(aux_mot)

        return current_dom_mot, intensities
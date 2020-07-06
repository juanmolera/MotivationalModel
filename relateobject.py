#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rospy import loginfo, logwarn, logerr
from motivational_model.classes.motivation import Motivation
from motivational_model.classes.homeostaticvariable import HomeostaticVariable
from motivational_model.classes.stimulus import Stimulus
from motivational_model.classes.action import Action
from motivational_model.classes.agent import Agent
from motivational_model.classes.effect import Effect
from motivational_model.classes.state import State

class RelateObject():

    def __get_int_list(self, related_var):
        """
        Transforms str data from database into int lists
        @ related_var str: data variable
        - Splits str (TEXT) data from database
        - Checks all entries are digits
        - Converts all entries to int
        """
        aux_var = list()
        x_list = list()

        if type(related_var) is unicode and "," in related_var:
            aux_var = related_var.split(",")
        elif bool(related_var):
            aux_var.append(related_var)

        for x in aux_var:

            if x.isdigit():
                x_list.append(x)
            else:
                rospy.logerr("related_var given is not correct")
            
        related_var = map(int, x_list)

        return related_var

    def create_hv_list(self, hv, std, time_step=1, logging=False):
        """
        Defining Homeostatic Variables and organizing them into a list
        @ hv dict: homeostatic variable data from database
        @ std dict: standard evolution parameter data from database
        """
        hv_list = list()

        for idx, i in enumerate(list(hv)):
            for idy, std_var in enumerate(list(std)):
                if std_var["id"] == i["std_evol"]:
                    params_std = {"te_id": std_var['type'], "slope": std_var['slope'], "tau": std_var['tau'], "step": std_var['step']}
                    break

            hv_list.append(HomeostaticVariable(i['id'], str(i['name']), i['initial_value'], i['ideal_value'], i['upper_limit'], i['lower_limit'], i['satisfaction_time'], params_std, time_step, logging))

        return hv_list

    def create_mot_list(self, mot, homeostatic_variables, stimuli, agents, logging=False):
        """
        Defining motivations and organizing them into a list
        @ mot dict: motivation data from database
        @ homeostatic_variables list: homeostatic variable objects list
        @ stimuli list: stimulus objects
        @ agents list: agent objects
        """
        mot_list = list()
        aux_var = None

        for idx, i in enumerate(list(mot)):
            aux_var = Motivation(i['id'], str(i['name']), i["threshold"], logging)

            for hv in homeostatic_variables:
                if hv.get_id() in self.__get_int_list(i["related_hv"]):
                    aux_var.add_hv(hv)

            for sti in stimuli:
                if sti.get_id() in self.__get_int_list(i["related_sti"]):
                    aux_var.add_sti(sti)

            for ag in agents:
                if ag.get_id() in self.__get_int_list(i["related_ag"]):
                    aux_var.add_ag(ag)

            mot_list.append(aux_var)
                    
        return mot_list

    def create_eff_list(self, effects, homeostatic_variables, std, con):
        """
        Defining Effects and organizing them into a list
        @ effects list: effect objects list
        @ homeostatic_variables list: homeostatic variable objects list
        @ std dict: standard evolution parameter data from database
        @ con dict: constancy data from database
        """
        eff_list = list()
        aux_var = None
        x_list = list()

        for idx, i in enumerate(list(effects)):
            for idy, std_var in enumerate(list(std)):
                if std_var["id"] == i["std_evol"]:
                    params_std = {"te_id": std_var['type'], "slope": std_var['slope'], "tau": std_var['tau'], "step": std_var['step']}
                    break
            
            aux_var = Effect(i['id'], i['constancy'], params_std)
            
            for idw, con_var in enumerate(list(con)):
                if con_var["id"] == i["constancy"]:
                    i["constancy"] = con_var["name"]
                    break

            for hv in homeostatic_variables:
                if hv.get_id() in self.__get_int_list(i["related_hv"]):
                    aux_var.add_hv(hv.get_id())

            eff_list.append(aux_var)

        return eff_list

    def create_sta_list(self, sta, std, time_step=1, logging=False):
        """
        Defining States and organizing them into a list
        @ sta dict: state data from database
        @ std dict: standard evolution parameter data from database
        """
        sta_list = list()

        for idx, i in enumerate(list(sta)):
            for idy, std_var in enumerate(list(std)):
                if std_var["id"] == i["activation_evol"]:
                    params_act = {"te_id": std_var['type'], "slope": std_var['slope'], "tau": std_var['tau'], "step": std_var['step']}
                if std_var["id"] == i["deactivation_evol"]:
                    params_deact = {"te_id": std_var['type'], "slope": std_var['slope'], "tau": std_var['tau'], "step": std_var['step']}

            sta_list.append(State(i['id'], str(i['name']), i["related_ag"], i["related_sti"], params_act, params_deact, time_step, logging))

        return sta_list

    def create_sti_list(self, sti, states):
        """
        Defining Stimuli and organizing them into a list
        @ sti dict: stimulus data from database
        @ states list: state objects list
        """
        sti_list = list()
        aux_states = list()

        for idx, i in enumerate(list(sti)):
            aux_states = list()
            for sta in states:
                if sta.get_related_sti() == i["id"]:
                    aux_states.append(sta)
                    if sta.get_id() == i["current_state"]:
                        current_stimuli_state = sta

            sti_list.append(Stimulus(i['id'], str(i['name']), current_stimuli_state, i['topic'], i['msg'], i['pkg']), aux_states)

        return sti_list

    def create_act_list(self, act, end_exo, effects, ag):
        """
        Defining Actions and organizing them into a list
        @ act dict: action data from database
        @ end_exo dict: endogenous/exogenous data from database
        @ effects list: effect objects list
        @ con dict: constancy data from database
        """
        act_list = list()
        aux_var = None
        x_list = list()

        for idx, i in enumerate(list(act)):
            aux_var = Action(i['id'], str(i['name']), i ['type'], i['related_ag'])

            for idy, e_var in enumerate(list(end_exo)):
                if e_var["id"] == i["type"]:
                    i["type"] = e_var["name"]
                    break

            for eff in effects:
                if eff.get_id() in self.__get_int_list(i["effects"]):
                    aux_var.add_eff(eff)
           
            act_list.append(aux_var)

        return act_list

    def create_ag_list(self, ag, states, actions, homeostatic_variables):
        """
        Defining Agents and organizing them into a list
        @ ag dict: agent data from database
        @ states list: state objects list
        @ actions list: action objects list
        @ homeostatic_variables list: homeostatic variable objects list
        """
        ag_list = list()
        aux_states = list()
        aux_actions = list()

        for idx, i in enumerate(list(ag)):
            aux_states = list()
            for sta in states:
                if sta.get_related_ag() == i["id"]:
                    aux_states.append(sta)
                    if sta.get_id() == i["current_state"]:
                        current_agent_state = sta
            aux_actions = list()
            for act in actions:
                if i['id'] == act.get_related_ag():
                    aux_actions.append(act)
        
            ag_list.append(Agent(i['id'], str(i['name']), current_agent_state, i['topic'], i['msg'], i['pkg'], aux_states, aux_actions))

        return ag_list
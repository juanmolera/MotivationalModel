#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error
import pandas as pd
import rospkg

pkg_name = "motivational_model"
rospack = rospkg.RosPack()

class DbLoader():
	
    def __init__(self):
        
        self.__database = rospack.get_path(pkg_name) + "/data/db/MM_db.db"
     
        # Creates database connection
        self.__conn = self.create_connection(self.__database)

    def create_connection(self, db_file):
        """ Creates a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
     
        return conn
    
    def get_data(self, string):
        """
        Relates database values with MotivationalModel data lists
        """
        variables = list()
        var = dict()

        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM " + string)
     
        rows = cur.fetchall()
        names = [description[0] for description in cur.description]

        for row in rows:
            var = dict()
            for idx, value in enumerate(list(row)):
                var[names[idx]] = value
            variables.append(var)

        return variables
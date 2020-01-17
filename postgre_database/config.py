#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 23:10:25 2020

@author: hugo
"""

from configparser import ConfigParser
 
 
def config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()  # create a parser
    parser.read(filename)    # read config file
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Section {0} not found in the {1} file".format(section, filename))
 
    return db

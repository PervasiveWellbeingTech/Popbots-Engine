#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 23:10:25 2020

@author: hugo & thierry
"""

from configparser import ConfigParser

from pathlib import Path
HERE = Path(__file__).parent.resolve()

 
 
def config(filename=str(HERE)+"/database.ini", section="postgresql"):
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

def config_string(filename=str(HERE)+"/database.ini", section="postgresql+psycopg2"):
    parser = ConfigParser()  # create a parser
    parser.read(filename)    # read config file 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0].upper()] = param[1]
        string = "{DB_TYPE}+{DB_CONNECTOR}://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}".format_map(db)
        return string    
    else:
        raise Exception("Section {0} not found in the {1} file".format(section, filename))
    

if __name__ == "__main__":
    print(config_string())
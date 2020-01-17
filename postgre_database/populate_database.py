#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 20:12:46 2020

@author: hugo
"""

import psycopg2
from config import config
import database_operations as dbo

DATA_FIXTURES = {
    "user_categories": [("human",), ("bot",)],
    "language_types": [("formal",), ("informal",)],
    "languages": [("english",)],
    "users": [
        ("Bob Dibub", 1),
        ("Checkin Bot", 2),
        ("Dunno Bot", 2),
        ("Sir Laughs-A-Bot", 2),
        ("Treat Yourself Bot", 2),
        ("Glass Half Full Bot", 2),
        ("Doom Bot", 2),
        ("Chill Bot", 2),
        ("Sherlock Bot", 2)        
    ],
    "human_users": [(1, "A123", 1, 1)],
    "features": [("yes",), ("no",), ("else",), ("none",), ("random",)],
    "selectors": [("yes?",), ("no?",), ("none",), ("random",)]
}

conn = None
try:
    params = config()                  # read the connection parameters
    conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
    
    # User categories
#    dbo.insert_into("user_categories", ("human",), conn)
#    dbo.insert_into("user_categories", ("bot",), conn)
    
    for table, data in DATA_FIXTURES.items():
        for values in data:
            dbo.insert_into(table, values, conn)
    
    conn.commit()  # commit the changes
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()

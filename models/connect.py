#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Created on Thu Jan 16 23:16:22 2020

@author: hugo
"""

import psycopg2
from config import config
 
def connect():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        params = config()  # read connection parameters
 
        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)
      
        cur = conn.cursor()  # create a cursor
        
        # execute a statement
        print("PostgreSQL database version:")
        cur.execute("SELECT version()")
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
        cur.close()  # close the communication with the PostgreSQL
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
 
 
if __name__ == "__main__":
    connect()

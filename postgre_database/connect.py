#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 23:16:22 2020

@author: hugo
"""

import psycopg2
from config import config
 
def connect():
    """ Connect to the PostgreSQL database server """
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

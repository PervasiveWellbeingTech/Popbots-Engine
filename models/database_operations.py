#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 02:11:10 2020

@author: hugo
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from models.core.config import config
import json

INSERT_QUERIES = {
    "user_categories": "INSERT INTO user_categories (name) VALUES (%s) RETURNING id;",
    "language_types": "INSERT INTO language_types (name) VALUES (%s) RETURNING id;",
    "languages": "INSERT INTO languages (name) VALUES (%s) RETURNING id;",
    "users": "INSERT INTO users (name, category_id) VALUES (%s, %s) RETURNING id;",
    "human_users": "INSERT INTO human_users (user_id, subject_id, language_type_id, \
        language_id) VALUES (%s, %s, %s, %s) RETURNING id;",
    "conversations": "INSERT INTO conversations (user_id) VALUES (%s) RETURNING id;",
    "contents": "INSERT INTO contents (text, user_id) VALUES (%s, %s) RETURNING id;",
    "keyboards": "INSERT INTO keyboards (name) VALUES (%s) RETURNING id;",
    "bot_contents": "INSERT INTO bot_contents (index, content_id, keyboard_id, \
        language_type_id, language_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
    "messages": "INSERT INTO messages (index, sender_id, receiver_id, content_id, \
        conversation_id, stressor) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
    "features": "INSERT INTO features (name) VALUES (%s) RETURNING id;",
    "feature_finders": "INSERT INTO feature_finders (index, feature_id) \
        VALUES (%s, %s) RETURNING id;",
    "selectors": "INSERT INTO selectors (name) VALUES (%s) RETURNING id;",
    "selector_finders": "INSERT INTO selector_finders (index, selector_id) \
        VALUES (%s, %s) RETURNING id;",
    "content_finders": "INSERT INTO content_finders (user_id, source_message_index, \
        message_index, bot_content_index, features_index, selectors_index) \
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
    "next_message_finders":"INSERT INTO next_message_finders (source_message_index, \
        next_message_index,user_id) VALUES (%s,%s,%s) RETURNING id;"

    
}


def insert_into(cur, table, values):
    """
    values is a tuple containing all values that we want to save in the given
    table. Order of values is important
    """
    sql_query = INSERT_QUERIES[table]
    last_id = None
    try:
        cur.execute(sql_query, values)
        
        last_id = cur.fetchone()[0]  # get the generated id back
        #cur.close()                  # close communication with the database
        print(f"Insertion (table {table}) successful")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
 
    return last_id


def select_from(cur, table,column, *where):
    """
    *where is an undefined number of tuples.
    Each tuple (a, b) will be used to make the condition WHERE a=b in the query
    (we could use a list, but it is maybe less convenient when there is only 
    one tuple)
    """
    
    conditions = " AND ".join(f"{field}='{value}'" for field, value in where)
    sql_query = f"SELECT {column} FROM {table} WHERE {conditions};"
    
    rows = None
    print(sql_query)
    try:
        
        cur.execute(sql_query)
        
        rows = cur.fetchall()
        cur.close()  # close communication with the database
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
 
    return rows


def select_from_join(cur,table,column,joins,wheres):
    """
    *where is an undefined number of tuples.
    Each tuple (a, b) will be used to make the condition WHERE a=b in the query
    (we could use a list, but it is maybe less convenient when there is only 
    one tuple)
    """

    conditions = " AND ".join(f"{field}={value}" for field, value in wheres)
 
    joins = " ".join(f"JOIN {join} ON {field}={value}" for join,field,value in joins)
    sql_query = f"SELECT {column} FROM {table} {joins} WHERE {conditions};"
    #print(f"""This is the SQL QUERY:\n{sql_query}""")
    rows = None
    try:
      
        cur.execute(sql_query)
        
        rows = cur.fetchall()
        cur.close()  # close communication with the database
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
 
    return rows

def custom_sql(cur,sql_query):
    """
    
    """
    rows = None
    print(sql_query)
    try:
      
        cur.execute(sql_query)
        
        rows = cur.fetchall()
        cur.close()  # close communication with the database
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
 
    return rows

def connection_wrapper(func,bool_json,*fparams):
        """
        dbfunc is either insert_into or select_from from the database operation function
        values needs to be unified for both insert and select from
        """

        conn = None
        
        
        try:
            #print(f"""Params are\n{fparams}\n with params lengh {len(fparams)}""")
            params = config()                  # read the connection parameters
            conn = psycopg2.connect(**params)  # connect to the PostgreSQL server

            if bool_json:
                cur= conn.cursor(cursor_factory=RealDictCursor) 
                query_result = func(cur,*fparams)
            else:
                cur=conn.cursor()
                query_result = func(cur,*fparams)
           

            conn.commit()  # commit the changes

            return query_result

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()


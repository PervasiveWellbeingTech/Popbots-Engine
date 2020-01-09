#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 00:06:10 2020

@author: hugo
"""

import sqlite3

INSERT_QUERIES = {
    "users": "INSERT INTO users (name, subject_id, category_id) VALUES (?, ?, ?)",
    "conversations": "INSERT INTO conversations (user_id) VALUES (?)",
    "contents": "INSERT INTO contents (text, user_id) VALUES (?, ?)",
    "messages": "INSERT INTO messages (sender_id, receiver_id, content_id, \
        conversation_id, message_index, stressor, variant) \
        VALUES (?, ?, ?, ?, ?, ?, ?)",
    "content_finders": "INSERT INTO content_finders (message_index, variant, \
        user_id, content_id, next_message_index) VALUES (?, ?, ?, ?, ?)"
}


def add(table, values, connection):
    """Used to add row in the given table (values is a tuple)"""
    
    query = INSERT_QUERIES[table]
    
    #print(query, values)
    
    cursor = connection.cursor()
    cursor.execute(query, values)
    last_row_id = cursor.lastrowid
    cursor.close()
    return last_row_id


def get_by(connection, table, *where):
    """
    *where is an undefined number of tuples.
    Each tuple (a, b) will be used to make the condition WHERE a=b in the query
    (we could use a list, but it is maybe less convenient when there is only 
    one tuple)
    """
    
    conditions = " AND ".join(f"{field}={value}" for field, value in where)
    query = f"SELECT * from {table} WHERE {conditions}"
    
    cursor = connection.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    return rows

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


def get_by(field, table, value, connection):
    query = f"SELECT * from {table} WHERE {field}={value}"
    
    cursor = connection.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    return rows


# TODO: improve this
def get_by_and(field_1, field_2, table, value_1, value_2, connection):
    query = f"SELECT * from {table} WHERE {field_1}={value_1} AND {field_2}={value_2}"
    
    cursor = connection.cursor()
    cursor.execute(query)
    
    rows = cursor.fetchall()
    return rows

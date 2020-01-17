#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 23:04:18 2020

@author: hugo
"""

import psycopg2
from config import config
 
 
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE user_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE language_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE languages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            subject_id VARCHAR(255),
            category_id INTEGER NOT NULL,
            language_type_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES user_categories (id),
            FOREIGN KEY (language_type_id) REFERENCES language_types (id),
            FOREIGN KEY (language_id) REFERENCES languages (id))
        """,
        """
        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id))
        """,
        """
        CREATE TABLE contents (
            id SERIAL PRIMARY KEY,
            index INTEGER NOT NULL,
            text TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            keyboard_id TEXT NOT NULL,
            language_type_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (language_type_id) REFERENCES language_types (id),
            FOREIGN KEY (language_id) REFERENCES languages (id))
        """,
        """
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            index INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,
            conversation_id INTEGER NOT NULL,
            stressor BOOLEAN NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (content_id) REFERENCES contents (id),
            FOREIGN KEY (conversation_id) REFERENCES conversations (id))
        """,
        """
        CREATE TABLE features (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE features_finder (
            id SERIAL PRIMARY KEY,
            index INTEGER NOT NULL,
            feature_id INTEGER NOT NULL,
            FOREIGN KEY (feature_id) REFERENCES features (id))
        """,
        """
        CREATE TABLE selectors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE selectors_finder (
            id SERIAL PRIMARY KEY,
            index INTEGER NOT NULL,
            selector_id INTEGER NOT NULL,
            FOREIGN KEY (selector_id) REFERENCES selectors (id))
        """,
        """
        CREATE TABLE content_finders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            source_message_index INTEGER,
            message_index INTEGER NOT NULL,
            bot_content_index INTEGER NOT NULL,
            features_index INTEGER NOT NULL,
            selectors_index INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (features_index) REFERENCES features_finder (id),
            FOREIGN KEY (selectors_index) REFERENCES selectors_finder (id))
        """,
        """
        CREATE TABLE next_message_finder (
            id SERIAL PRIMARY KEY,
            source_message_index INTEGER NOT NULL,
            next_message_index INTEGER NOT NULL)
        """
        )
        
    conn = None
    try:
        params = config()                  # read the connection parameters
        conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
        cur = conn.cursor()
        
        # create table one by one
        for command in commands:
            cur.execute(command)
               
        cur.close()    # close communication with the PostgreSQL database server
        conn.commit()  # commit the changes
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == "__main__":
    create_tables()

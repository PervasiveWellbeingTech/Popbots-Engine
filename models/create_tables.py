# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 23:04:18 2020
#!/usr/bin/env python3
@author: hugo
"""

import psycopg2
from core.config import config
 
 
def create_tables():
    """Create tables in the PostgreSQL database"""
    
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
            category_id INTEGER NOT NULL,
            desactivated BOOLEAN NOT NULL,
            FOREIGN KEY (category_id) REFERENCES user_categories (id))
        """,
        """
        CREATE TABLE human_users (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            subject_id VARCHAR(255) NOT NULL,
            language_type_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            experiment_group VARCHAR(255) NULL,
            timezone varchar null,
            FOREIGN KEY (user_id) REFERENCES users (id) on delete cascade,
            FOREIGN KEY (language_type_id) REFERENCES language_types (id),
            FOREIGN KEY (language_id) REFERENCES languages (id))
        """,        
        """
        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            stressor text,
            datetime timestamp not NULL default CURRENT_TIMESTAMP,
            closed BOOLEAN,
            timeout_threshold int Null,
            conversational_state varchar NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) on delete cascade
            )
        """,
        """
        CREATE TABLE stressor (

            id SERIAL PRIMARY KEY,
            stressor_text text NULL,
            conversation_id int not NULL,
            stress_level text NULL,
            
            category0 text NULL,
            category1 text NULL,
            category2 text NULL,
            category3 text NULL,
            category4 text NULL,
            category5 text NULL,
            category6 text NULL,
            covid_category text NULL,
            
            covid_probability float(6),
            probability0 float(6),
            probability1 float(6),
            probability2 float(6),
            probability3 float(6),
            probability4 float(6),
            probability5 float(6),

            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            

        );

        """, 
        """
        CREATE TABLE contents (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            
            ) 
        """,
        """
        CREATE TABLE next_message_finders (
            id SERIAL PRIMARY KEY,
            source_message_index INTEGER NOT NULL,
            next_message_index INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) on delete cascade
            )
        """,
        """
        CREATE TABLE keyboards (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL)
        """,
        """
        CREATE TABLE content_finders (
            id SERIAL PRIMARY KEY,
            message_index INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) on delete cascade
            )
        """,
        """
        CREATE TABLE bot_contents (
            id SERIAL PRIMARY KEY,
            content_id INTEGER NOT NULL REFERENCES contents (id),
            keyboard_id INTEGER NOT NULL,
            language_type_id INTEGER NOT NULL,
            language_id INTEGER NOT NULL,
            content_finders_id INTEGER NOT NULL,
            FOREIGN KEY (content_finders_id) REFERENCES content_finders (id) on delete cascade,
            FOREIGN KEY (keyboard_id) REFERENCES keyboards (id),
            FOREIGN KEY (language_type_id) REFERENCES language_types (id),
            FOREIGN KEY (language_id) REFERENCES languages (id))
        """,
        """
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            index INTEGER,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,
            conversation_id INTEGER NOT NULL,
            answering_time INTEGER NULL,
            tag VARCHAR,
            datetime timestamp not NULL default CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (content_id) REFERENCES contents (id),
            FOREIGN KEY (conversation_id) REFERENCES conversations (id))
        """,
        """
        CREATE TABLE intents (
            id SERIAL PRIMARY KEY,
            synonyms VARCHAR,
            regex VARCHAR,
            name VARCHAR(255) NOT NULL)
        """,
        """
        CREATE TABLE triggers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        
        """
        CREATE TABLE context (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL)
        """,
        
        
       
        """
        CREATE TABLE context_finders (
            id SERIAL PRIMARY KEY,
            content_finders_id INTEGER NOT NULL,
            context_id INTEGER NOT NULL,
            FOREIGN KEY (content_finders_id) REFERENCES content_finders (id) on delete cascade,
            FOREIGN KEY (context_id) REFERENCES context (id) on delete cascade)
        """,
        """
        CREATE TABLE intent_finders (
            id SERIAL PRIMARY KEY,
            content_finders_id INTEGER NOT NULL,
            intent_id INTEGER NOT NULL,
            FOREIGN KEY (content_finders_id) REFERENCES content_finders (id) on delete cascade,
            FOREIGN KEY (intent_id) REFERENCES intents (id) on delete cascade)
        """,
        """
        CREATE TABLE trigger_finders (
            id SERIAL PRIMARY KEY,
            content_finders_id INTEGER NOT NULL,
            trigger_id INTEGER NOT NULL,
            outbound BOOLEAN NOT NULL,
            FOREIGN KEY (content_finders_id) REFERENCES content_finders (id) on delete cascade,
            FOREIGN KEY (trigger_id) REFERENCES triggers (id) on delete cascade)
        """,
        """
        CREATE TABLE reminders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content_id INTEGER not null,
            creation_date timestamp not null default CURRENT_TIMESTAMP,
            reminder_time timestamp not null, 
            reminder_type varchar null,
            executed boolean null,
            expired boolean null,
            
            FOREIGN KEY (user_id) REFERENCES users (id) on delete cascade,
            FOREIGN KEY (content_id) REFERENCES contents (id) on delete cascade
        );
        """, 

        """
            INSERT INTO "public"."user_categories" ("id", "name") VALUES ('1', 'Human');
            INSERT INTO "public"."user_categories" ("id", "name") VALUES ('2', 'Bot');
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
        print("Tables created")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
 
if __name__ == "__main__":
    create_tables()

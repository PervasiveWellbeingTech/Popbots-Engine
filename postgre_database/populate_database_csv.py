#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 20:12:46 2020

@author: Thierry Lincoln
"""

import psycopg2
from config import config
import pandas as pd
from bot_management import add_bot_content

bot_name = 'glass_half_full_bot'
bot_id = 6
base_csv_path = '/Users/thierrylincoln/Box/PopBots/Popbots-Refactoring/'

content_finder_path = base_csv_path+"content_finders_csv/content_finders_{}.csv".format(bot_name)
content_finder = pd.read_csv(content_finder_path)

next_message_finder_path = base_csv_path+"next_message_finders_csv/next_message_finders_{}.csv".format(bot_name)
next_message_finder = pd.read_csv(next_message_finder_path)

previous_message_finder_path = base_csv_path+"previous_message_finders_csv/previous_message_finders_{}.csv".format(bot_name)
previous_message_finder = pd.read_csv(previous_message_finder_path)



conn = None
try:
    params = config()                  # read the connection parameters
    conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
    
    # User categories
#    dbo.insert_into("user_categories", ("human",), conn)
#    dbo.insert_into("user_categories", ("bot",), conn)
    for index,item in content_finder.iterrows():
        print("Add a bot message")
       
        content = item.content
        index = item.msg_index
        next_index = None
        next_bot_id = bot_id
        next_content_type = item.next_content_type
        language_type_id = item.language_type_id
        language_id = item.language_id
        keyboard_id = item.keyboard_id
        features_index =item.features_finder_index
        selectors_index =item.next_selectors
        source_message_index =None

        add_bot_content(conn,content, index,bot_id, next_index, next_bot_id, next_content_type,keyboard_id,language_id,language_type_id,features_index,selectors_index,source_message_index)
    
    for index,item in next_message_finder.iterrows():
        dbo.insert_into(conn,"next_message_finders",(item.msg_index,item.next_msg_index,bot_id))



    conn.commit()  # commit the changes
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()

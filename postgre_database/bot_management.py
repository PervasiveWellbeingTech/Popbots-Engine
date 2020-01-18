#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 22:39:00 2020

@author: hugo
"""

import psycopg2
from config import config
import database_operations as dbo


"""
def new_bot():
    bot_name = input("Bot name: ")
    dbop.add("users", (bot_name, None, 2), connection)
    print(f"{bot_name} added")    


def add_bot_message(content, index, variant, bot_id, next_index, next_bot_id, next_content_type, connection=connection):
    content_id = dbop.add("contents", (content, bot_id, None), connection)
    dbop.add("content_finders", (index, variant, bot_id, content_id, next_index, next_bot_id, next_content_type), connection)
    print("Message added")


def display_messages(bot_id, index, depth):
    messages = dbop.get_by(connection, "content_finders", ("user_id", bot_id), ("message_index", index))

    for message in messages:
        message_id, message_index, variant, user_id, content_id, next_message_index, next_bot_id, next_content_typ = message
        content = dbop.get_by(connection, "contents", ("id", content_id))[0][1]
#        print(f"{2*(depth-1)*' '}|__ {content}")
        print(f"{depth*' |'}__({message_index}-{variant}) {content}")
        print(f"{(depth+1)*' |'}")
        if user_id == next_bot_id:
            display_messages(user_id, next_message_index, depth + 1)


def display_messages_tree(bot_id):
    display_messages(bot_id, 1, 1)

"""


def manage_bot(bot):
    bot_id, bot_name, _ = bot
    print(f"\n-> Manage {bot_name}")
    
    # TODO replace this:
    keyboard_id, language_type_id, language_id = 1, 1, 1
    
    # To this kind of verification
#    keyboard_ids = dbo.select_from(conn, "keyboards", ("name", "default"))
#    if keyboard_ids:
#        keyboard_id = keyboard_ids[0][0]
#    else:
#        print("WARNING: No default keyboard id")
#        # throw exception
    
    messages = dbo.select_from(conn, "content_finders", ("user_id", bot_id))
    if not messages:
        bot_content_index = 1
        source_message_index = None
        message_index = 1
        features_index = 1
        selectors_index = 1
        
        # Formal
        content_id = dbo.insert_into(conn, "contents", ("START formal", bot_id)) 
        dbo.insert_into(conn, "bot_contents", (bot_content_index, content_id,
                                               keyboard_id, language_type_id, language_id))
        dbo.insert_into(conn, "content_finders", (bot_id, source_message_index,
                                                  message_index, bot_content_index, features_index,
                                                  selectors_index))
        
        # Informal
        content_id = dbo.insert_into(conn, "contents", ("START informal", bot_id)) 
        dbo.insert_into(conn, "bot_contents", (bot_content_index, content_id,
                                               keyboard_id, language_type_id + 1, language_id))
        dbo.insert_into(conn, "content_finders", (bot_id, source_message_index,
                                                  message_index, bot_content_index, features_index,
                                                  selectors_index))
        
        print("INFO: A START message has been automatically created")

#content_finders 
#(user_id, source_message_index, message_index, bot_content_index, features_index, selectors_index)

#bot_contents
#(index, content_id, keyboard_id, language_type_id, language_id)

    while True:
        print("\n- To see the messages tree, type t")
        print("- To add a message, type +")
        print("- To quit, type q")
        command = input()
        
        if command == "q":
            break
        elif command == "+":
            print("Add a bot message")
        elif command == "t":
            #display_messages_tree(bot_id)
            print("Not implemented yet")
        else:
            print("Unknown command")


if __name__ == "__main__":
    conn = None
    try:
        params = config()                  # read the connection parameters
        conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
 
        print("BOTS MANAGEMENT")
        bot_category_ids = dbo.select_from(conn, "user_categories", ("name", "bot"))
        if bot_category_ids:
            bot_category_id = bot_category_ids[0][0]
        else:
            print("WARNING: No category id for bot")
            # TODO: throw exception

        while True:
            bots = dbo.select_from(conn, "users", ("category_id", bot_category_id))
            
            if not bots:
                print("No bot yet")
            
            for bot in bots:
                bot_id, bot_name, _= bot
                print(f"  - n°{bot_id} {bot_name}")
            
            print("\n- To manage a bot, type the bot number")
            print("- To add a bot, type +")
            print("- To quit, type q")
            command = input()
            
            if command == "q":
                break
            elif command == "+":
                #new_bot()
                print("Not implement yet")
            else:
                print("Manage bot...")
                bot_id = command
                bots = dbo.select_from(conn, "users", ("id", bot_id))
                if bots:
                    manage_bot(bots[0])
                else:
                    print("No bot with this id")

        
        conn.commit()  # commit the changes
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

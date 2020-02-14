



import telegram
#from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.error import NetworkError, Unauthorized
from main import response_engine
import time
import datetime
import random
import string
#import sys, getopt
#import os, nltk
import re

#!popbotsenv/bin/python
from collections import defaultdict
#from os import system
from telegrame.utils import Params, Config, Modes, find_keyword, find_name, find_id, find_problem
#from get_response import get_response_dict
#from get_response_informal import get_response_dict_informal
#from pymongo import MongoClient
import telegram
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.error import NetworkError, Unauthorized
from time import sleep
import sys
import traceback

#from messenger import Message
TIMEOUT_SECONDS = 3600

def log(msg):
    print(msg)

class TelegramBot():
    """
    Implementation of the bot.

    Initialization parameter:
        token (string) -- Telegram bot token

    Class parameters:
        self.bot (telegram.bot) -- telegram bot object
        self.reply_dict (dict) -- dictionary containing all responses
        self.params (utils.Params) -- fixed parameters
        self.config (utils.Config) -- bot configuration

        self.user_history(defaultdict) -- temporary dictionary of user to user history
        self.user_name_dict(defaultdict) -- user_id to name dictionary
        self.user_bot_state_dict (defaultdict) -- user_id to bot state dict (defaults to a random bot)
        self.user_problem_dict(dict) -- user_id to problem dictionary
        self.user_parameters_dict(defaultdict) -- dictionary that stores all parameters used by the bots.
    """

    def __init__(self, token): #, reply_dict, **kwargs):
        print("Bot initialization.")
        #initialize telegram bot
        self.bot = telegram.Bot(token)
        #self.msg_engine  = Message()
        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None

        self.params = Params()
        self.config = Config()
        self.message_queues = {}


        keyboards =[telegram.InlineKeyboardButton("Choose for me")]+[
                                telegram.InlineKeyboardButton(name) for idx, name in enumerate(self.params.bot_name_list) if idx not in {4,7}]
        self.bots_keyboard = [ [x,y] for x,y in zip(keyboards[0::2], keyboards[1::2]) ]
        if len(keyboards)%2 ==1:
            self.bots_keyboard.append([keyboards[-1]])


    def send_message(self,user_id,text_response,keyboard):
        log("Trying to send the message")
        log(text_response)
        for res in text_response:
            self.bot.sendChatAction(chat_id=user_id, action = telegram.ChatAction.TYPING)
            sleep(min(len(res)/20,2.5))
            self.bot.send_message(chat_id=user_id, text=res, reply_markup = keyboard)
    
    def get_keyboard(self,reply_markup):

        if(reply_markup['type'] == 'choice'):
            return telegram.ReplyKeyboardMarkup(self.bots_keyboard, resize_keyboard=reply_markup['resize_keyboard'])
        elif(reply_markup['type']=='inlineButton'):
            return telegram.ReplyKeyboardMarkup([[telegram.InlineKeyboardButton(reply_markup['text'])]], resize_keyboard= reply_markup['resize_keyboard'])
        elif(reply_markup['type']=='normal'):
            return telegram.ReplyKeyboardRemove()
        else:
            return telegram.ReplyKeyboardRemove()

    
    def process_message(self, user_id, query):
        
        response  = response_engine(user_id,user_message=query)
        keyboard = telegram.ReplyKeyboardRemove() #self.get_keyboard(response['reply_markup'])
        
        log(response['img'])
        if not response['img']:
            self.send_message(user_id,response['response_list'],keyboard)

        elif response['img'] and len(response['response_list'])>0:
            try:
                self.bot.send_photo(chat_id=user_id, photo=response['img'],timeout=10)
                log('Sended the photo')
            except:
                log("Enable to send the picture")
            try:
                self.send_message(user_id,response['response_list'],keyboard)
                log('Sended the message')
            except:
                log("Failed to send the message")

            
    @run_async
    def callback_handler(self, update, context):
            """
            Wrapper function to call the message handler

            This function will also catch and print out errors in the console
            
            """

            try:
                message = update.message
                if message.chat_id in self.message_queues:
                    message_queue = self.message_queues[message.chat_id] 
                    message_queue.append({'text':message.text,'date':message.date}) 
                else :
                    self.message_queues[message.chat_id] = [{'text':message.text,'date':message.date}]
                    message_queue = self.message_queues[message.chat_id]
                queue_size = len(message_queue)
                
                while message_queue:
                    if queue_size < len(message_queue):
                        break
                    self.bot.sendChatAction(chat_id=message.chat_id, action = telegram.ChatAction.TYPING)
                    delta = datetime.datetime.utcnow() - message_queue[-1]['date'] # calculating UTC time delta
                    if delta.seconds > 2:
                        message_queue = []
                        self.process_message(message.chat_id, message.text)   
            
            except:
                exc_info = sys.exc_info()
            finally:
                traceback.print_exception(*exc_info)
                del exc_info
            #print(sys.exc_info()[0])
            # traceback.print_stack()

            #self.process_updates(update)

    def error_callback(self,bot, update, error):
        raise error

    def run(self):
        """
        Run the bot.
        """
        updater = Updater(token,use_context = True)
        dp = updater.dispatcher # Get the dispatcher to register handlers 
        dp.add_handler(MessageHandler(Filters.text, self.callback_handler))
        dp.add_handler(CommandHandler("start", self.callback_handler))
        dp.add_handler(CommandHandler("switch", self.callback_handler))

        #dp.add_error_handler(self.error_callback)
        print("Running Bot ... (Ctrl-C to exit)")
        updater.start_polling()


if __name__ == '__main__':
    # Telegram Bot Authorization Token
    f = open('telegrame/token.txt')
    token = f.read()
    print(token)
    bot = TelegramBot(token)
    bot.run()
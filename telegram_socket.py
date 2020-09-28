import os
import re
import time
import datetime
import random
import string
import sys
import traceback
from time import sleep
from collections import defaultdict
from time import time
import datetime
import pytz

from controllers.main import dialog_flow_engine
from utils import log,timed


import telegram
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram.error import NetworkError, Unauthorized

from threading import Thread, current_thread


#from messenger import Message
TIMEOUT_SECONDS = 3600
QUEUE_TIME_THRESHOLD = 2

class TelegramBot():

    def __init__(self, token): 

        self.bot = telegram.Bot(token)
        self.message_queues = {}
        self.is_replying = {}

    @timed
    def send_message(self,user_id,text_response,keyboard,image):
        log('DEBUG',f"Trying to send a message block to user id {user_id} ")
        len_text_response_no_image = len([value for value in text_response if not re.match('image',value)])
        i=0
        log('DEBUG',text_response)
        for res in text_response:
            self.bot.sendChatAction(chat_id=user_id, action = telegram.ChatAction.TYPING)
            #
            #sleep(min(len(res)/25,1.5))
            
            
            if not re.match('image',res):
                i+=1
            
                
                if i == len_text_response_no_image:
                    self.bot.send_message(chat_id=user_id, text=res, reply_markup = keyboard)

                else:
                    self.bot.send_message(chat_id=user_id, text=res, reply_markup = telegram.ReplyKeyboardRemove())
            else:
                try: 
                    if "png" in image.name:
                        self.bot.send_photo(chat_id=user_id, photo=image,timeout=10)
                    elif "gif" in image.name:
                        self.bot.send_animation(chat_id=user_id,animation=image, timeout=10)
                except Exception as error:
                    log('ERROR',f"Image fail image: {image} to send to user id {user_id} with error {error}")
                    
                log('DEBUG',f"Image sent to user id {user_id}")
            
            log('DEBUG',f"Delaying the next message")
            if not i == len_text_response_no_image:
                
                self.bot.sendChatAction(chat_id=user_id, action = telegram.ChatAction.TYPING)

                if len(res)<25:
                    sleep(1)
                elif len(res) > 25 and len(res)<75:
                    sleep(2)
                elif len(res) > 75 and len(res)<125:
                    sleep(3)
                else:
                    sleep(4)
        log('DEBUG',f"Message block sent to user id {user_id}")

        self.is_replying[user_id] = False
    
    def get_keyboard(self,reply_markup):

        if(reply_markup['type'] == 'choice'):
            return telegram.ReplyKeyboardRemove()
        elif(reply_markup['type']=='inlineButton'):
            buttons = reply_markup['text'].split("|")
            keyboards =[telegram.KeyboardButton(name) for name in buttons]
            
            if (any([True if len(x)>20 else False for x in buttons])):
                keyboards_formatted = [[x] for x in keyboards]
            else:
                keyboards_formatted = [ [x,y] for x,y in zip(keyboards[0::2], keyboards[1::2]) ] #cut the list to make sure two by two buttons appears
                
                if len(keyboards)%2 ==1:
                    keyboards_formatted.append([keyboards[-1]]) # add the first button in one line

            return telegram.ReplyKeyboardMarkup(keyboards_formatted, resize_keyboard= reply_markup['resize_keyboard'])
        elif(reply_markup['type']=='default'):
            return telegram.ReplyKeyboardRemove()
        else:
            return telegram.ReplyKeyboardRemove()
    
    @run_async
    def process_message(self, user_id, datetime_info,query):
        """
        """
        response  = dialog_flow_engine(user_id,datetime_info,user_message=query)
        keyboard = self.get_keyboard(response['reply_markup'])
        image = response['img']

        #print("__________________________ Current thread ________" + str(current_thread()))
        
        if len(response['response_list'])>0:
            self.send_message(user_id,response['response_list'],keyboard,image)

        


            
    @run_async
    def callback_handler(self, update, context):
            """
            Wrapper function to call the message handler

            This function will also catch and print out errors in the console
            
            """
            #print("__________________________ Current thread ________" + str(current_thread()))


            try:
                
                
                message = update.message

                incoming_delta = datetime.datetime.utcnow() - message.date

                datetime_info = {"incoming_delta":incoming_delta,"sent_datetime":message.date}

                log('DEBUG',f"Message received and was sent at {message.date}, delay to receive is {incoming_delta.seconds} ")
                log('TIME TOOK',f'Time delta for incoming telegram_message in file telegram_socket.py is {incoming_delta.seconds} s')
                
                if message.chat_id not in self.is_replying:
                    self.is_replying[message.chat_id] = False
                    


                
                if message.chat_id in self.message_queues:
                    message_queue = self.message_queues[message.chat_id]

                    if not self.is_replying[message.chat_id] == True: 
                        message_queue.append({'text':message.text,'date':datetime.datetime.utcnow()}) 
                    else:
                        log('INFO',f"We just completely ignored user's message {message.text}")
                else :
                    self.message_queues[message.chat_id] = [{'text':message.text,'date':datetime.datetime.utcnow()}]
                    message_queue = self.message_queues[message.chat_id]
                queue_size = len(message_queue)
                
                while message_queue:
                    sleep(0.1) # without this it may call the telegram api too much
                    if queue_size < len(message_queue):
                        break
                    #self.bot.sendChatAction(chat_id=message.chat_id, action = telegram.ChatAction.TYPING)
                    delta = datetime.datetime.utcnow() - message_queue[-1]['date'] # calculating UTC time delta
                    if delta.seconds > QUEUE_TIME_THRESHOLD and not self.is_replying[message.chat_id] == True :
                        final_message = ""
                        final_message = " ".join([element['text'] for element in message_queue])
                        self.is_replying[message.chat_id] = True
                        self.process_message(message.chat_id,datetime_info, final_message)
                        message_queue.clear()
                        
            
            except (BaseException,Exception) as error:
                log('ERROR',''.join(traceback.TracebackException.from_exception(error).stack.format()))
                
      
            except:
                exc_info = sys.exc_info()

            finally:

                traceback.print_exception(*exc_info)
                del exc_info
    

    def error_callback(self,bot, update, error):
        raise error

    def run(self):
        """
        Run the bot.
        """
        updater = Updater(token,use_context = True)
        
        dp = updater.dispatcher # Get the dispatcher to register handlers 
        dp.run_async(self.callback_handler)
        dp.run_async(self.process_message)
        
        dp.add_handler(CommandHandler("start", self.callback_handler))

        dp.add_handler(MessageHandler(Filters.text, self.callback_handler))
        dp.add_handler(CommandHandler("switch", self.callback_handler))

        dp.add_error_handler(self.error_callback)
        log('INFO',"Started telegram bot socket ... (Ctrl-C to exit)")
        updater.start_polling()
        #updater.idle()


if __name__ == '__main__':
    # Telegram Bot Authorization Token Must be set in env variables 

    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if token is None:
        log('ERROR','Not token has been found, telegram socket cannot be launched')
        raise ValueError

    bot = TelegramBot(token)
    bot.run()
import os
import pytz
import traceback

import telegram
from utils import log,timed
import datetime
from time import sleep

from models.user import HumanUser
from models.main import push_message, database_push,delconv,create_human_user,create_conversation,push_stressor
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from models.utils import get_user_id_from_name



from threading import Thread, current_thread
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest


token = os.getenv("TELEGRAM_BOT_TOKEN")
if token is None:
    log('ERROR','Not token has been found, telegram socket cannot be launched')
    raise ValueError

bot = telegram.Bot(token)


thread_session = ThreadSessionRequest() # thread safe SQL Alchemy session
session = thread_session.s # sql alchemy session one per thread


while True:
    try:
        # fetch all human users, if their last activity is more than a day ago, and the time is 7pm at their local time then send a message
        all_users = session.query(HumanUser).all()

        bot_id = get_user_id_from_name("Greeting Module")

        for user in all_users:
            
            user_timezone = user.timezone if user.timezone is not None else 'UTC'
            user_id = user.user_id
            #2. Fetching the lastest active conversations 
            conversation = session.query(Conversation).filter_by(user_id = user_id).order_by(Conversation.datetime.desc()).first()

            if conversation is None:

                log('DEBUG', f"No conversation for user: {user.name} with id: {user_id}")
            else:

                if user.name == "Thieryy":
                    tz = pytz.timezone(user.timezone)
                    utc = pytz.timezone('UTC')
                    
                    nowUTC = datetime.datetime.now(utc)
                    now_local = nowUTC.astimezone(tz)

                    last_conversation_dt = conversation.datetime.astimezone(utc)

                    conversation_delta =  nowUTC - last_conversation_dt

                    text=f"Hey {user.name}! I just want to check up on how you're doing."

                    if conversation_delta > datetime.timedelta(minutes=5):
                        new_conversation = create_conversation(session,user_id)

                        push_message(session,text,user_id,index=None,receiver_id=user_id,sender_id=bot_id,conversation_id = new_conversation.id,tag = "nudge")

                        new_conversation.closed = True
                        session.commit()

                        keyboard =telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton("Hi")]], resize_keyboard= True)
                        bot.send_message(chat_id=user.user_id, text=text, reply_markup = keyboard)
                    else:
                        log('DEBUG', f"Conversations for this user are recent {conversation_delta}")
    except BaseException as error:
      error_traceback = error.__traceback__
      log('ERROR', str(error) + str(''.join(traceback.format_tb(error_traceback))))
    
    sleep(30)
import os
import pytz
import traceback
import random
import telegram
from utils import log,timed
import datetime
from time import sleep

from models.user import HumanUser
from models.main import push_message, database_push,delconv,create_human_user,create_conversation,push_stressor
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from models.utils import get_user_id_from_name
from models.reminders import Reminders
from sqlalchemy import func,and_

from sqlalchemy.dialects import postgresql


from threading import Thread, current_thread
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest


from random import randrange
from datetime import timedelta

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)





token = os.getenv("TELEGRAM_BOT_TOKEN")
if token is None:
    log('ERROR','Not token has been found, telegram socket cannot be launched')
    raise ValueError

bot = telegram.Bot(token)


thread_session = ThreadSessionRequest() # thread safe SQL Alchemy session
session = thread_session.s # sql alchemy session one per thread
small_talk = ["Hi","Hello","Hey there"]

reminders_list = ["Just reminding you that you can talk to us when you feeling stressed.","We are here whenever you need us to talk about what's bothering you.", "It's good to regularly check on your stress. We are here when you need us."]

current_user_id = [1069201240,666742053,384644196,886580524,583828528]



def send_reminder_message(reminder,session):

    text_raw = session.query(Content).filter_by(id =reminder.content_id).first().text
    response_list = text_raw.replace("\xa0"," ").strip().replace("'","\\'").split("\nm")
    print(response_list)
    
    response_list = [eval(f""" f'{text}'""") for text in response_list]



    new_conversation = create_conversation(session,reminder.user_id)

    push_message(session,".".join(response_list),reminder.user_id,index=None,receiver_id=reminder.user_id,sender_id=bot_id,conversation_id = new_conversation.id,tag = "reminder")

    new_conversation.closed = True
    session.commit()

    keyboard =telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton("Hi")]], resize_keyboard= True)

    for message in response_list:
        bot.send_message(chat_id=user.user_id, text=message, reply_markup = keyboard)
        sleep(1)



while True:
    try:
        thread_session = ThreadSessionRequest() # thread safe SQL Alchemy session
        session = thread_session.s # sql alchemy session one per thread
        # fetch all human users, if their last activity is more than a day ago, and the time is 7pm at their local time then send a message
        all_users = session.query(HumanUser).all()

        bot_id = get_user_id_from_name("Greeting Module")

        for user in all_users:

            try:
            
                #fetching user's timzone, default to UTC
                user_timezone = user.timezone if user.timezone is not None else 'UTC'
                log('DEBUG',f"User timezone is {user_timezone}")

                user_id = user.user_id

                tz = pytz.timezone(str(user_timezone))
                utc = pytz.timezone('UTC')
                
                nowUTC = datetime.datetime.now(utc)
                now_local = nowUTC.astimezone(tz)
                
                today =str(now_local.strftime('%Y-%m-%d'))
                tomorrow = str((now_local+timedelta(days=1)).strftime('%Y-%m-%d'))
                
                log("INFO", f"Today's date for user {user.user_id} is {today}")
                log("INFO", f"Tomorrow's date for user {user.user_id} is {tomorrow}")

                # setting up the two time interval we would want to send reminders: 9-16h (day) and another time 17-22h ( evening )
                day_in,day_out = now_local.replace(hour=9,minute=0),now_local.replace(hour=16,minute=0)
                evening_in,evening_out = now_local.replace(hour=17,minute=0),now_local.replace(hour=22,minute=0)

                # getting those time in UTC - because the conversations timestamps are stored in UTC
                day_in_utc, day_out_utc = day_in.astimezone(utc),day_out.astimezone(utc)
                evening_in_utc,evening_out_utc = evening_in.astimezone(utc),evening_out.astimezone(utc)

                
                if user.user_id in current_user_id: #limiting this to the user list Right now
                    
                    todays_reminder = session.query(Reminders).filter(and_(Reminders.user_id==user.user_id,Reminders.reminder_time.between(today,tomorrow))).all()
                    
                    
                    # schedule reminders before 9 am every day 
                    if now_local.hour < 9: 
                        log('DEBUG', f"Local time for participant {user.user_id} is less than 9 at {now_local.hour} ")

                        todays_reminder = session.query(Reminders).filter(and_(Reminders.user_id==user.user_id,Reminders.reminder_time.between(today,tomorrow))).all()

                        if len(todays_reminder) <2:
                            
                            # we need to create the reminders one for the day and one for the evening
                            
                            # 1 pick a random time from between 9-16h (day) and another time 17-22h ( evening )  for the intervention nudges
                            day_time = random_date(day_in,day_out)
                            evening_time = random_date(evening_in,evening_out)
                            
                            log('INFO',f'It is now {now_local} locally for user {user.user_id}')
                            log('INFO',f'A day reminder will be set at {day_time} for user {user.user_id}')
                            log('INFO',f'A evening time reminder will be set at {evening_time} for user {user.user_id}')

                            # 2 Create the reminder by assembling a random combination of small_talk and reminder
                            text_day = str(random.choice(small_talk) +". " + str(random.choice(reminders_list)))
                            text_evening = str(random.choice(small_talk) +". "+ str(random.choice(reminders_list)))

                            # 2.1 add these content to the database
                            content_day = Content(text=text_day,user_id=user_id)
                            session.add(content_day)
                            content_evening = Content(text=text_evening,user_id=user_id)
                            session.add(content_evening)

                            session.commit()
                            
                            # Create the reminder for the following content
                            day_reminder = Reminders(user_id=user.user_id,content_id=content_day.id,creation_date = now_local.replace(tzinfo=None), reminder_time = day_time.replace(tzinfo=None),reminder_type='Day',executed=False,expired=False)
                            evening_reminder = Reminders(user_id=user.user_id,content_id=content_evening.id,creation_date = now_local.replace(tzinfo=None),reminder_time = evening_time.replace(tzinfo=None),reminder_type='Evening',executed=False,expired=False)
                            
                            session.add(day_reminder)
                            session.add(evening_reminder)
                            session.commit()

                        elif len(todays_reminder) > 2:
                            log('DEBUG',f'ERROR {len(todays_reminder)} reminders has been set for this user for date {today}')
                        else:
                            log('DEBUG',f'{len(todays_reminder)} reminders has been set for this user for date {today} ')
                            pass # we are not supposed to do anything before 9 am, since no reminders can be set at that particular time
                    else: #after 9 am, if reminder for the user hasn't been set during that particular time frame, well the user won't be reminded this day

                        if todays_reminder is not None:

                            
                            for reminder in todays_reminder:
                                if not (reminder.expired or reminder.executed): # boolean NOR only enter if False, False
                                    if now_local - tz.localize(reminder.reminder_time) > datetime.timedelta(seconds=0) :# if the timedelta difference between now and reminder is positive it means that the reminder need to be processed
                                        #check if the user already interacted with the bots in the current timeframe
                                        

                                        if reminder.reminder_type == "Day":
                                            
                                            conversation_day = session.query(Conversation).filter(and_(Conversation.user_id==user.user_id,Conversation.datetime.between(day_in_utc.strftime('%Y-%m-%d %H:%M:%S'), day_out_utc.strftime('%Y-%m-%d %H:%M:%S')))).all()
                                            if len(conversation_day)>0:
                                                log('INFO',f"User {user.user_id} has already talked with the bot during the day")
                                                reminder.expired = True # setting the reminder as expired because the user did interact with the platform in the given time frame
                                            else:
                                                send_reminder_message(reminder,session)
                                                reminder.executed = True
                                            
                                            session.commit()  
                                        
                                        elif reminder.reminder_type == "Evening":
                                            conversation_day = session.query(Conversation).filter(and_(Conversation.user_id==user.user_id,Conversation.datetime.between(evening_in_utc.strftime('%Y-%m-%d %H:%M:%S'), evening_out_utc.strftime('%Y-%m-%d %H:%M:%S')))).all()
                                            
                                            if len(conversation_day)>0:
                                                reminder.expired = True # setting the reminder as expired because the user did interact with the platform in the given time frame
                                                log('INFO',f"User {user.user_id} has already talked with the bot during the evening")
                                            else:
                                                send_reminder_message(reminder,session)
                                                reminder.executed = True
                                            session.commit()  

                                        else:
                                            log('INFO',f"Unknown type reminder has been set, type: {reminder.reminder_type} , this reminder will be set as expired")
                                            reminder.expired = True
                                            session.commit()
                                    
            except BaseException as error:
                error_traceback = error.__traceback__
                log('ERROR', str(error) + str(''.join(traceback.format_tb(error_traceback))))

                    #log('DEBUG', f"Todays reminders are {}")

    except BaseException as error:
      error_traceback = error.__traceback__
      log('ERROR', str(error) + str(''.join(traceback.format_tb(error_traceback))))
    del thread_session
    sleep(30)
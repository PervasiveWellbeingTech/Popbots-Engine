import re
import random
import time
import sys
import traceback
import os

from datetime import datetime

import sqlalchemy,psycopg2 # import to get errors

from exceptions.badinput import BadKeywordInputError
from exceptions.nopossibleanswer import NoPossibleAnswer
from exceptions.authoringerror import AuthoringError

from controllers.message import get_bot_response

from models.user import HumanUser,Users
from models.utils import get_user_id_from_name
from models.core.config import config_string
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from models.stressor import Stressor,populated_stressor
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest


from utils import log,timed
from threading import Thread, current_thread

import string



def find_name(input_str):
    """
    A simple algorithm to extract names.
    Parameters:
        input_str(str) -- string containing the name
    """

    for each in ['i am', 'i\'m',"i’m",'this is', 'name is', 'my name is','it is','you can call me','i am named after']:
        _index = input_str.lower().find(each)
        if _index != -1:
            result = input_str.lower()[_index + len(each)+1:]
            result = result.split()[0]
            for each_punc in list(string.punctuation):
                result = result.replace(each_punc,"")
            if len(result) > 0 and len(result) < 20:
                return result.capitalize()
    return input_str.capitalize().split()[0]


def database_push(session,element):
    session.add(element)
    session.commit()
    return element.id

@timed
def push_message(session,text,user_id,index,receiver_id,sender_id,conversation_id,tag):
    content_user = Content(text=text,user_id=user_id)
    content_id_user  = database_push(session,content_user)
    message_user = Message(index=index,receiver_id=receiver_id,sender_id=sender_id,content_id=content_id_user,conversation_id = conversation_id,datetime=datetime.now(),tag=tag)
    _ = database_push(session,message_user) 

def delconv(session,user_id):
    conversation = session.query(Conversation).filter_by(user_id=user_id,closed = False).order_by(Conversation.datetime.desc()).first()
    if conversation:
        conversation.closed = True
        session.commit()


def change_bot(session,current_bot_id,destination_bot_name,next_index=0):
    if destination_bot_name is None:
        possible_bot = get_bot_ids(session,current_bot_id,"Greeting Module") #### Replace with the correct module
        bot_id =  possible_bot[random.randint(0,len(possible_bot)-1)] 
    else:
        bot_id = get_user_id_from_name(destination_bot_name)

        if bot_id == current_bot_id:
            log('INFO',f'You are switching to the exact same bot with bot_id: {bot_id} ')
    

    return next_index,bot_id

@timed
def create_human_user(session,user_id,user_message):
    """
        Create user object, binds subject id to it (to be completed), set the language, language_type, initializes the user_name

    """
    user = HumanUser(user_id=user_id)
    subject_id = re.findall(r'\d+', user_message)
    if subject_id:
        user.subject_id = subject_id[0]
    else:
        user.subject_id = "0000"
    user.language_id = 1 # for english
    user.language_type_id = 1 # for formal 
    user.category_id = 1
    possible_group = ["Group","Moderator"]
    user.experiment_group = possible_group[random.randint(0,1)]
    
    user.name = "Human" # this is the default
    session.add(user)
    session.commit()

    return user

@timed
def create_conversation(session,user_id):
    dt = datetime.now()
    conversation = Conversation(user_id=user_id,datetime=dt,closed=False)
    _ = database_push(session,conversation)

    return conversation


def get_bot_ids(session,exclude_id,exclude_name):
    return [x.id for x in session.query(Users).filter(Users.category_id==2,~Users.name.contains('Module')) if (x.name not in {exclude_name} and x.id not in {exclude_id})]
def get_bot_names(session,exclude_id,exclude_name):
    return [x.name for x in session.query(Users).filter(Users.category_id==2,~Users.name.contains('Module')) if (x.name not in {exclude_name} and x.id not in {exclude_id})]


def image_fetcher(bot_text):
    
    start = bot_text.find("$img$") + len("$img$")
    end = bot_text.find("$img$",start)
    substring = bot_text[start:end]
    img = None
    bot_text = bot_text.replace("$img$"+substring+"$img$","")
    if os.path.exists('./img/{}.png'.format(substring)):
        img = open('./img/{}.png'.format(substring), 'rb')
    elif os.path.exists('./img/{}'.format(substring)):
        img = open('./img/{}'.format(substring), 'rb')

    
    return bot_text,img

def push_stressor(session,conv_id):
    print(conv_id)
    stressor1 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor1').first()
    stressor2 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor2').first()
    stressor3 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor3').first()

    print(stressor1)
    stressor_list = [stressor1,stressor2,stressor3]
    print(stressor_list)
    stressor_text = '. '.join(x.text for x in stressor_list if x)

    stressor = populated_stressor(stressor_text,conv_id = conv_id)

    session.add(stressor)
    session.commit()

    log('INFO',f'Stressor: {stressor_text} sucessfully added to conversation id {conv_id}')

    
def find_string_between_tag(string,start,end):
    return string[string.find(start)+len(start):string.rfind(end)]

@timed
def response_engine(session,user_id,user_message):
    """
        Given a user_id and user_message, response engine fetches the latest message from the bot given branching options.
        Handles special commands (Hi, \switch, \start ), handle active conversations. Records the interactions If needed calls the classifier. Choose the bot. 
        Sets the outbound command dict in order to skip responses or not. 

    Parameters:
        session (object) -- sql alchemy session
        user_id (int) -- user id, defined by telegram , slack 
        user_message(str) -- incoming user message


    Returns:
         TO BE FILLED(list/dict) --  
    """

    log('DEBUG',f"Incoming message is: "+str(user_message))
    
    #initializes some variables
    latest_bot_index = None
    bot_id = None
    tag = None
    bot_tag = None
    image = None
    command = {"skip":False,"stack":True}
    onboarding_module = "OnboardingModerator Module"
    
    
    #1. Fetching the active user or create one if needed
    user = session.query(HumanUser).filter_by(user_id=str(user_id)).first() 
    if user is not None:
        log('DEBUG',f'User is known as: {user.name}')
    else:
        user = create_human_user(session,user_id,user_message)
        log('DEBUG',f"User with id: {user.id} has been created")
        
        # since we know that the user is unknown, we can directly push them to the onboarding Module
        bot_id = get_user_id_from_name("Greeting Module") # needs to be replaced with onboarding when design team is done with it
        latest_bot_index = 0 
        latest_bot_message = None
        
    #2. Fetching the lastest active conversations 
    conversation = session.query(Conversation).filter_by(user_id=user_id,closed = False).order_by(Conversation.datetime.desc()).first()
    
    if conversation is not None:
        log('DEBUG',f"Conversation detected with the id {conversation.id}") 

        CONVERSATION_INIT = False

        if (datetime.now() - conversation.datetime).seconds > 3600 : #Time out We should create an error that is send the user ? 
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)
            CONVERSATION_INIT = True

            bot_id = get_user_id_from_name("Greeting Module")
            latest_bot_index = 0
            latest_bot_message = None

    else: 
        log('DEBUG',f"Warning the conversation id is none and the message is {user_message}")
        conversation = create_conversation(session,user_id)
        CONVERSATION_INIT = True

        bot_id = get_user_id_from_name("Greeting Module")
        latest_bot_index = 0
        latest_bot_message = None

    # 3.0  Handling special cases ( Hi , /start)
    # handling /start, the user wants to restart the onboarding process
    if re.match(r'/start',user_message): #force restart the onboarding process

        if conversation and not CONVERSATION_INIT: # closing the previous conversation
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)

        if re.findall(r'\d+',user_message):
            user.subject_id = re.findall(r'\d+',user_message)[0]
            session.commit()



        if "moderator" in user_message:
            log("INFO","User has been rolled in Moderator Group")
            user.experiment_group = "Moderator"
        elif "group" in user_message:
            log("INFO","User has been rolled in Group Group")
            user.experiment_group = "Group"
        
        session.commit()
        onboarding_module = "Onboarding"+user.experiment_group+" Module"

        
        
        bot_id = get_user_id_from_name(onboarding_module)

        latest_bot_index = 0
        latest_bot_message = None

    #handling Hi the user want to force restart a conversation
    elif re.match(r'Hi',user_message): 

        if conversation and not CONVERSATION_INIT: # closing the previous conversation
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)
        
        bot_id = get_user_id_from_name("Greeting Module")
        latest_bot_index = 0
        latest_bot_message = None
        

    # handle the special switch case, if switch, we change the bot, else we find the latest active bot. 
    if re.match(r'/switch', user_message): #switch
        
        latest_bot_index,bot_id = change_bot(session,bot_id,'Switch Module')
    else:

        #4. Fetching the lastest active message in the conversation 
        latest_bot_message = session.query(Message).filter_by(receiver_id=user_id,conversation_id=conversation.id).order_by(Message.id.desc()).first() # finding the lastest message
        

        # general case, means that we did not enter in /start or Hi
        if latest_bot_message is not None and latest_bot_index is None:
            latest_bot_index = latest_bot_message.index 
            bot_id = latest_bot_message.sender_id
            log('DEBUG',f"Found a previous message pointing to {latest_bot_index} and was send by bot_id {bot_id}")

        # we dont have a last bot message and latest_index is none. (safeguard) is switches bot to recover. (could throw an error instead)
        elif latest_bot_message is None and latest_bot_index is None: # there is no message 
            log('DEBUG',f"Should not have entered in the no message, no in itialized scenario but did")
            latest_bot_index,bot_id = change_bot(session,bot_id,None)

        #latest_bot_index could be none because of bad storage of the previous_index in the last message
        # SHOULD ADD LOG messages here
        if latest_bot_index is not None:
            pass 

        else:

            latest_bot_index,bot_id = change_bot(session,bot_id,None)  # could throw an error here instead of switching to another bot

    


    stressor = session.query(Stressor).filter_by(conversation_id = conversation.id).order_by(Stressor.conversation_id.desc()).first() # fetching the stressor in the conversation if exists. 
    
    #fetching the bot_user object
    bot_user = session.query(Users).filter_by(id = bot_id).first() 
    
    # create a dict of variables to be used to do the next message selection process
    selector_kwargs = {"user_response":user_message,"stressor":stressor,"user":user} 

    #fetching the bot text response, the keyboards and eventual triggers
    bot_text,current_index,keyboard,triggers = get_bot_response(session,bot_user=bot_user,latest_bot_index=latest_bot_index,selector_kwargs=selector_kwargs)
    

    log('DEBUG',f'Bot text would be: {bot_text}, with triggers: {triggers}')

    ## handle special flag in bot scrips 

    if "<SWITCH>" in bot_text:
        command = {"skip":True,"stack":False} 
        bool_trigger = [True if "~" in x else False for x in triggers]

        if any(bool_trigger):
            
            next_bot_name = [x for x in triggers if "~" in x][0].replace("~","")
            next_index = re.findall(r'\d+',next_bot_name)
            next_bot_name = result = re.sub(r"\d+", "", next_bot_name)
            
            if next_bot_name == "choose_bot" or user_message=="Choose for me":
                log('INFO',f"Switching to bot or module {next_bot_name}, from id {bot_id}")
                current_index,bot_id = change_bot(session,current_bot_id=bot_id,destination_bot_name=None)
            
            elif next_bot_name == "user_input":
                log('INFO',f"Switching to bot or module {next_bot_name}, from id {bot_id}")
                current_index,bot_id = change_bot(session,current_bot_id=bot_id,destination_bot_name=user_message)
            elif next_index != []:

                current_index,bot_id = change_bot(session,current_bot_id=bot_id,destination_bot_name=next_bot_name,next_index=next_index[0])

            else:
                 
                current_index,bot_id = change_bot(session,current_bot_id=bot_id,destination_bot_name=next_bot_name)

            log("DEBUG",f"Switching to a new bot with bot_id = {bot_id} and name {next_bot_name} ")
        else:
            log('ERROR',f"Trying to switch to a new bot but there is no ~something in triggers")
            raise AuthoringError(bot_user.name,current_index,"Trying to switch to a new bot but there is no valid ~ tilda")
    
    elif bot_text == "<START>":
        command = {"skip":True,"stack":False}
    
    elif bot_text == "<SKIP>":
        command = {"skip":True,"stack":False}
    
    #closing the conversation if needed
    if "<CONVERSATION_END>" in bot_text: 
        log('DEBUG',f'Ending conversation id {conversation.id} for user {user.id}')
        conversation.closed = True
        session.commit()
        command = {"skip":False,"stack":False}
    
    # if the response is empty switch bot, add the message to db but keep
    if bot_text == "" or bot_text is None:
        log("ERROR" ,f"bot_text was empty or None, forcing jump to a new bot")
        current_index,bot_id = change_bot(session,bot_id,None)
        command = {"skip":True,"stack":False}
        
    
    #fetching the bot_user
    bot_user = session.query(Users).filter_by(id = bot_id).first()

    
    #handle triggers
    try:

        if len(triggers)>0:
            for trigger in triggers:
                if trigger == "#user.name":
                    user.name = find_name(user_message)

                elif "#" in trigger:
                    trigger = trigger.replace("#","")
 

                    if len(trigger.split(".")) ==2:
                        class_name,class_variable = trigger.split(".")
                        #exec(trigger+"="+str(user_message) )
                        setattr(locals()[class_name],class_variable,user_message)
                    else: # we assume that it is one
                    
                        locals()[trigger]=user_message
                elif "tag:" in trigger:
                    tag = re.sub('tag:','',trigger)
                elif "bot_tag" in trigger:
                    bot_tag = re.sub('bot_tag:','',trigger)
                elif "!stressor" in trigger:
                    push_stressor(session = session,conv_id = conversation.id)#conversation.id)
                elif "!skip_response" in trigger:
                    command = {"skip":True,"stack":True}


    except Exception as error:
        tb = traceback.TracebackException.from_exception(error)
        log('ERROR',":loudspeaker: [FATAL Trigger ERROR]" + str(error)+str(''.join(tb.stack.format())))

      

    #pushing messages in database
    push_message(session,text=user_message,user_id=user_id,index=None,receiver_id=bot_id,sender_id=user_id,conversation_id=conversation.id,tag=tag) # pushing user message
    push_message(session,text=bot_text,user_id=bot_id,index=current_index,receiver_id=user_id,sender_id=bot_id,conversation_id=conversation.id,tag=bot_tag) # pushing the bot response

    # fetching lastest bot/intervention entity of a conversation 
    latest_bot = session.query(Users).join(Message,Users.id==Message.receiver_id).filter(Users.category_id==2,Users.name.contains('Bot'),Message.conversation_id == conversation.id).order_by(Message.id.desc()).first()

    # parsing the data before sending
    response_list = bot_text.replace("\xa0"," ").strip().replace("'","\\'").split("\\n")
    log('DEBUG', response_list)
    # handle images if required
    for index,text in enumerate(response_list):
        if "$img$" in text:
            response_list[index],image = image_fetcher(text)
            response_list.insert(max(0,index),'image')
            

    # formatting the text with the neccessary info eg: user:name, etc...
    try: 
        templist = []
        for res in response_list:
            templist.append(eval(f"f'{res}'"))
        response_list = templist
        
    except BaseException as error:
        log('ERROR',f"String interpolation for {bot_user.id},{bot_user.name} failed due to: {error}")
        raise AuthoringError(bot_user.name,current_index,f"Interpolation problem from {find_string_between_tag(bot_text,'{','}')} variable.")



    # formating keyboard text
    try:
        keyboard = eval(f"f'{str(keyboard)}'")
    except BaseException as error:

        log('ERROR',f"Keyboard interpolation for {bot_user.id},{bot_user.name} failed due to: {error}")
        raise AuthoringError(bot_user.name,current_index,f"Interpolation problem for keyboard for {find_string_between_tag(keyboard,'{','}')} variable.")


    #handle keyboards add reply markup
    if keyboard=="default":
        keyboard_object = {'type':'default','resize_keyboard':True,'text':""} #no keyboard
    
    elif keyboard == "all_bots":

        possible_bot = get_bot_names(session,None,None) #### Replace with the correct module
        possible_bot.insert(0,"Choose for me")
        keyboard = '|'.join(possible_bot)
        keyboard_object = {'type':'inlineButton','resize_keyboard':True,'text':keyboard}
    else:
        keyboard_object = {'type':'inlineButton','resize_keyboard':True,'text':keyboard}  #
        
    
    
    if latest_bot is None:
        bot_name = bot_user.name
    else:
        bot_name = latest_bot.name


    session.commit()
    log('DEBUG','------------------------END OF MESSAGE ENGINE------------------------')

    if re.match(r'/start',user_message) or re.match(r'Hi',user_message):
        user_message = "user_greeting"
        

    return command,response_list,image,bot_name,keyboard_object,user_message



def dialog_flow_engine(user_id,user_message):
    """
        Dialog flow engine can stack many responses from response engine.
        It pushes to telegram what needs to be pushed, and ignores what can be passed ? <START>, <CONVERSATION_END> these are useful for managing the overall
        but the user does not need to see them. 

        Also receive , and process any error fom the system. therefore we see the try/except

    """

    
    log('INFO',f"Current thread is: {current_thread()}")
    
    thread_session = ThreadSessionRequest() # thread safe SQL Alchemy session
    session = thread_session.s # sql alchemy session one per thread

    # define empty dict for telegram_sockets
    keyboard_object = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
    response_dict={'response_list':[],'img':None,'reply_markup':keyboard_object,'bot_name':""}

    try:
        command = {"skip":True,"stack":False} # initialize the command parameter, which is update by response_engine after
        
        while command["skip"]==True: # loop and does not send the message until skip == False


            command,response_list,image,bot_name,keyboard_object,user_message  = response_engine(session,user_id,user_message)
            if image is not None:
                response_dict['img']= image
            if command["stack"] == True: # handles two message in a row
                
                response_dict['response_list'] = response_dict['response_list'] + response_list

            
            
            response_dict['reply_markup'] = keyboard_object
            response_dict['bot_name'] = bot_name
        return response_dict
    
    except BadKeywordInputError as error:
        log('ERROR',error)
        response_dict={'response_list':["Oops, sorry for being not precise enought...","I expected: '"+ "' or '".join(set(error.intents))+"' as an answer for the latest question","Can you answer again please?"],'img':None,'command':None,'reply_markup':keyboard_object,'bot_name':"Onboarding Bot"}
        delconv(session,user_id)
        return response_dict

    except AuthoringError as error:
        log('ERROR',":x: [FATAL AUTHORING ERROR] "+str(error))
        response_dict={'response_list':["My creators left me short of answer for this one","I'll probably go to sleep until they fix my issue",'Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':keyboard_object,'bot_name':"Onboarding Bot"}
        delconv(session,user_id)
        return response_dict

    except NoPossibleAnswer as error:
        keyboard_object = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
        log('ERROR',":loudspeaker: [FATAL ERROR]" +str(error))
        delconv(session,user_id)

  
        return {'response_list':['It seems that my bot brain lost itself in the flow...','Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':keyboard_object,'bot_name':"Onboarding Bot"}
    
    except BaseException as error:
        keyboard_object = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
        response_dict={'response_list':['It seems that my bot brain lost itself in the flow...','Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':keyboard_object,'bot_name':"Onboarding Bot"}
        
        tb = traceback.TracebackException.from_exception(error)
        log('ERROR',":loudspeaker: [FATAL BASE ERROR]" + str(error)+str(''.join(tb.stack.format())))
        delconv(session,user_id)


        return response_dict
    
    finally:
        del thread_session


import re
import random
import time
import sys
import traceback

from datetime import datetime


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
        #session.commit()


def change_bot(session,current_bot_id,destination_bot_name):
    next_index=0
    if destination_bot_name is None:
        possible_bot = get_bot_ids(session,current_bot_id,"Greeting Module") #### Replace with the correct module
        bot_id =  possible_bot[random.randint(0,len(possible_bot)-1)] 
    else:
        bot_id = get_user_id_from_name(destination_bot_name)

        if bot_id == current_bot_id:
            log('INFO',f'You are switching to the exact same bot with bot_id: {bot_id} ')
    
    content_index = session.query(ContentFinders).filter_by(user_id=bot_id,message_index = next_index).first().id

    return next_index,bot_id,content_index

@timed
def create_human_user(session,user_id,user_message):
    user = HumanUser(user_id=user_id)
    user.subject_id = re.findall(' ([0-9]+)', user_message)
    user.language_id = 1 # for english
    user.language_type_id = 1 # for formal 
    user.category_id = 1
    
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
    
    bot_text = bot_text.replace("$img$"+substring+"$img$","")

    img = open('./img/{}.png'.format(substring), 'rb')
    
    return bot_text,img

def push_stressor(session,conv_id):
    print(conv_id)
    stressor1 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor1').first()
    stressor2 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor2').first()
    stressor3 = session.query(MessageContent).filter_by(conversation_id = conv_id,tag = 'stressor3').first()

    print(stressor1)
    stressor_list = [stressor1,stressor2,stressor3]
    print(stressor_list)
    stressor_text = ' '.join(x.text for x in stressor_list if x)

    stressor = populated_stressor(stressor_text,conv_id = conv_id)

    session.add(stressor)
    session.commit()

    log('INFO',f'Stressor: {stressor_text} sucessfully added to conversation id {conv_id}')

    
    

@timed
def response_engine(session,user_id,user_message):

    log('DEBUG',f"Incoming message is: "+str(user_message))
    

    next_index = None
    bot_id = None
    tag = None
    image = None
    command = {"skip":False,"stack":True}
    

    #1. Fetching the active user or create one if needed
    user = session.query(HumanUser).filter_by(user_id=str(user_id)).first() 
    if user is not None:
        log('DEBUG',f'User is known as: {user.name}')
    else:
        user = create_human_user(session,user_id,user_message)
        log('DEBUG',f"User with id: {user.id} has been created")
        
        bot_id = get_user_id_from_name("Greeting Module")
        next_index = 0
        message = None
        
    #2. Fetching the lastest active conversations 
    conversation = session.query(Conversation).filter_by(user_id=user_id,closed = False).order_by(Conversation.datetime.desc()).first()
    
    if conversation:
        log('DEBUG',f"Conversation detected with the id {conversation.id}") 

        CONVERSATION_INIT = False

        if (datetime.now() - conversation.datetime).seconds > 3600 : #Time out
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)
            CONVERSATION_INIT = True

    else: 
        log('DEBUG',f"Warning the conversation id is none and the message is {user_message}")
        conversation = create_conversation(session,user_id)
        CONVERSATION_INIT = True

        bot_id = get_user_id_from_name("Greeting Module")
        next_index = 0
        message = None

    #handling /start, the user wants to restart the onboarding process
    if re.match(r'/start',user_message): #force restart the onboarding process

        if conversation and not CONVERSATION_INIT: # closing the previous conversation
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)
        bot_id = get_user_id_from_name("Onboarding Module")
        next_index = 0
        message = None

    #handling Hi the user want to force restart a conversation
    elif re.match(r'Hi',user_message): 

        if conversation and not CONVERSATION_INIT: # closing the previous conversation
            conversation.closed = True
            session.commit()
            conversation = create_conversation(session,user_id)
        
        bot_id = get_user_id_from_name("Greeting Module")
        next_index = 0
        message = None

    
    
    message = session.query(Message).filter_by(receiver_id=user_id,conversation_id=conversation.id).order_by(Message.id.desc()).first() # finding the lastest message
    

    # general case, means that we did not enter in /start or Hi
    if message is not None and next_index is None:
        next_index = message.index 
        bot_id = message.sender_id
        log('DEBUG',f"Found a previous message pointing to {next_index} and was send by bot_id {bot_id}")

    elif message is None and next_index is None: # there is no message 
        log('DEBUG',f"Should not have entered in the no message, no in itialized scenario but did")
        next_index,bot_id,content_index = change_bot(session,bot_id,None)

    #next_index could be none because of bad storage of the previous_index in the last message
    if next_index is not None:  
        content_index = session.query(ContentFinders).filter_by(user_id=bot_id,message_index = next_index).first().id
    else:
        next_index,bot_id,content_index = change_bot(session,bot_id,None) 

    if re.match(r'/switch', user_message): #switch
        
        next_index,bot_id,content_index = change_bot(session,bot_id,'Switch Module')

    #include here the problem with problem parser
    problem = "that"

    stressor = session.query(Stressor).filter_by(conversation_id = conversation.id).first()
    
    bot_user = session.query(Users).filter_by(id = bot_id).first()

    #fetching the bot text response, the keyboards and eventual triggers
    bot_text,current_index,keyboard,triggers = get_bot_response(bot_user=bot_user,next_index=next_index,user_response=user_message,content_index=content_index,stressor_object=stressor)
    



    log('DEBUG',f'Bot text would be: {bot_text}, with triggers: {triggers}')

    ## handle special flag in bot scrips 

    if "<SWITCH>" in bot_text:
        command = {"skip":True,"stack":False}
        bool_trigger = [True if "~" in x else False for x in triggers]

        if any(bool_trigger):
            
            next_bot_name = [x for x in triggers if "~" in x][0].replace("~","")
            
            if next_bot_name == "choose_bot" or user_message=="Choose for me":
                log('INFO',f"Switching to bot or module {next_bot_name}, from id {bot_id}")
                current_index,bot_id,content_index = change_bot(session,current_bot_id=bot_id,destination_bot_name=None)
            
            elif next_bot_name == "user_input":
                log('INFO',f"Switching to bot or module {next_bot_name}, from id {bot_id}")
                current_index,bot_id,content_index = change_bot(session,current_bot_id=bot_id,destination_bot_name=user_message)
            
            else:
                current_index,bot_id,content_index = change_bot(session,current_bot_id=bot_id,destination_bot_name=next_bot_name)

            log("DEBUG",f"Switching to a new bot with bot_id = {bot_id} and name {next_bot_name} ")
        else:
            log('ERROR',f"Trying to switch to a new bot but there is no ~something in triggers")
    
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
        current_index,bot_id,content_index = change_bot(session,bot_id,None)
        command = {"skip":True,"stack":False}
        
    
    #fetching the bot_user
    bot_user = session.query(Users).filter_by(id = bot_id).first()

    
    #handle triggers
    try:

        if len(triggers)>0:
            for trigger in triggers:
                if "#" in trigger:
                    trigger = trigger.replace("#","") 

                    if len(trigger.split(".")) ==2:
                        class_name,class_variable = trigger.split(".")
                        #exec(trigger+"="+str(user_message) )
                        setattr(locals()[class_name],class_variable,user_message)
                    else: # we assume that it is one
                    
                        locals()[trigger]=user_message
                elif "tag:" in trigger:
                    tag = re.sub('tag:','',trigger)
                elif "!stressor" in trigger:
                    push_stressor(session = session,conv_id = conversation.id)#conversation.id)
                elif "!skip_response" in trigger:
                    command = {"skip":True,"stack":True}


    except Exception as error:
        log('ERROR',f"Trigger error"+error)

    # handle images if required
    if "$img$" in bot_text:
        bot_text,image = image_fetcher(bot_text)
        
        

    log("DEBUG",f"The user id is: {user_id}")

    if current_index is None:
        log('ERROR',"Something went wrong current_index is None ???? Will log bad data")

    #pushing messages in database
    push_message(session,text=user_message,user_id=user_id,index=None,receiver_id=bot_id,sender_id=user_id,conversation_id=conversation.id,tag=tag) # pushing user message
    push_message(session,text=bot_text,user_id=bot_id,index=current_index,receiver_id=user_id,sender_id=bot_id,conversation_id=conversation.id,tag=None) # pushing the bot response


    
    # parsing the data before sending
    response_list = bot_text.replace("\xa0"," ").strip().replace("'","\\'").split("\\n")
    
    # formatting the text with the neccessary info eg: user:name, etc...
    try: 
        templist = []
        for res in response_list:
            templist.append(eval(f"f'{res}'"))
        response_list = templist
        
    except BaseException as error:
        log('ERROR',f"String interpolation for {bot_user.id},{bot_user.name} failed due to: {error}")


    # formating keyboard text
    try:
        keyboard = eval(f"f'{str(keyboard)}'")
    except BaseException as error:

        log('ERROR',f"Keyboard interpolation for {bot_user.id},{bot_user.name} failed due to: {error}")

    #handle keyboards add reply markup
    if keyboard=="default":
        reply_markup = {'type':'default','resize_keyboard':True,'text':""} #no keyboard
    
    elif keyboard == "all_bots":

        possible_bot = get_bot_names(session,None,None) #### Replace with the correct module
        possible_bot.insert(0,"Choose for me")
        keyboard = ','.join(possible_bot)
        reply_markup = {'type':'inlineButton','resize_keyboard':True,'text':keyboard}
    else:
        reply_markup = {'type':'inlineButton','resize_keyboard':True,'text':keyboard}  #
        
    bot_name = bot_user.name


    session.commit()
    log('DEBUG','------------------------END OF MESSAGE ENGINE------------------------')


    return command,response_list,image,bot_name,reply_markup



def dialog_flow_engine(user_id,user_message):

    
    log('INFO',f"Current thread is: {current_thread()}")
    
    thread_session = ThreadSessionRequest() # thread safe SQL Alchemy session
    session = thread_session.s


    reply_markup = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
    response_dict={'response_list':[],'img':None,'reply_markup':reply_markup,'bot_name':""}

    try:
        command = {"skip":True,"stack":False}
        while command["skip"]==True:

            command,response_list,image,bot_name,reply_markup  = response_engine(session,user_id,user_message)

            if command["stack"] == True:
                if image is not None:
                    response_dict['response_list'].append("image")
                    response_dict['img'] = image
                response_dict['response_list'] = response_dict['response_list'] + response_list

            
            
            response_dict['reply_markup'] = reply_markup
            response_dict['bot_name'] = bot_name
            print(response_dict['response_list'])
        return response_dict
    
    except BadKeywordInputError as error:
        log('ERROR',error)
        response_dict={'response_list':["Oops, sorry for being not precise enought...","I expected: '"+ "' or '".join(set(error.features))+"' as an answer for the latest question","Can you answer again please?"],'img':None,'command':None,'reply_markup':reply_markup,'bot_name':"Onboarding Bot"}
        session.rollback()
        delconv(session,user_id)
        return response_dict

    except AuthoringError as error:
        log('ERROR',":x: [FATAL AUTHORING ERROR] "+str(error))
        response_dict={'response_list':["My creators left me short of answer for this one","I'll probably go to sleep until they fix my issue",'Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':reply_markup,'bot_name':"Onboarding Bot"}
        session.rollback()
        delconv(session,user_id)
        return response_dict

    except NoPossibleAnswer as error:
        reply_markup = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
        log('ERROR',":loudspeaker: [FATAL ERROR]" +str(error))
        session.rollback()
        delconv(session,user_id)
        return {'response_list':['It seems that my bot brain lost itself in the flow...','Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':reply_markup,'bot_name':"Onboarding Bot"}
    
    except BaseException as error:
        reply_markup = {'type':'inlineButton','resize_keyboard':True,'text':"Hi"}
        response_dict={'response_list':['It seems that my bot brain lost itself in the flow...','Sorry for that, say "Hi" to start a new conversation'],'img':None,'command':None,'reply_markup':reply_markup,'bot_name':"Onboarding Bot"}
        
        tb = traceback.TracebackException.from_exception(error)
        log('ERROR',":loudspeaker: [FATAL ERROR]" + str(error)+str(''.join(tb.stack.format())))
        session.rollback()
        delconv(session,user_id)
        return response_dict
    
    finally:
        session.close()
        del thread_session


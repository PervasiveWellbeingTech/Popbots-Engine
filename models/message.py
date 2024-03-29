"""
The intent of this file is to collect all the different SQL queries needed to execute the message process
"""
from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from,custom_sql
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from utils import log,timed,flatten


def fetch_synonyms_regex(intent_name):

    """

    Function which fetches the synonyms and the eventual regex associated with it
    Parameters:
        intent_name (string) -- name of an intent
    Returns:
        synonyms(list),regex (string) -- true if keyword is found.

    """

    synonyms_regexes = connection_wrapper(select_from,True,"intents","intents.synonyms,intents.regex",("intents.name",intent_name),)
    synonyms = synonyms_regexes[0]['synonyms']
    regex = synonyms_regexes[0]['regex']

    synonyms = synonyms.split("|")
    
    return synonyms,regex


def fetch_context_name(message_index):
    """
    Query the SQL database and return the context list associated with a particular message content index

    Parameters:
        msg_index (string) -- index of the particular message 
        bot_id (int) -- id of the current bot

    Returns:
        context_list (list/dict) --  
    """
    #we need to actualize the context to the lastest state
    context_list = connection_wrapper(select_from_join,True,"context_finders","ALL context.name",
        (("context","context_finders.context_id","context.id"),),
        (("context_finders.content_finders_id",message_index),))
    return context_list

def fetch_triggers_name(message_index,outbound):
    """
    Query the SQL database and return the trigger list associated with a particular bot_id at a certain index

    Parameters:
        msg_index (string) -- index of the particular message 

    Returns:
        triggers (list/dict) --  
    """
    #we need to actualize the triggers to the lastest state
    triggers = connection_wrapper(select_from_join,True,"trigger_finders","ALL triggers.name",
        (("triggers","trigger_finders.trigger_id","triggers.id"),),
        (("trigger_finders.content_finders_id",message_index),("trigger_finders.outbound",outbound),))
    
    return triggers

def fetch_intent_name(message_index):
    #we need to actualize the context to the lastest state
    intents = connection_wrapper(select_from_join,True,"intent_finders","ALL intents.name",
        (("intents","intent_finders.intent_id","intents.id"),),
        (("intent_finders.content_finders_id",message_index),))
    return intents[0]



def fetch_next_indexes(bot_id,index):
    next_indexes = [index[0] for index in connection_wrapper(select_from,False,"next_message_finders","next_message_index",
        ("user_id",bot_id),("source_message_index",index))]
    return next_indexes

def fetch_next_contents(bot_id,next_indexes):
    """
    Based on all the parameters this function queries the DB to get the current messages 
    Params that should not be forgotten include : language_id,language_type_id,

    """
    content_list=[]
    for next_index in next_indexes:
        content_list.append(connection_wrapper(select_from_join,True,"content_finders","distinct on (content_finders.id) content_finders.id,contents.text,keyboards.name",
            (("bot_contents","content_finders.id","bot_contents.content_finders_id"),("contents","bot_contents.content_id","contents.id"),("keyboards","bot_contents.keyboard_id","keyboards.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("message_index",next_index)))) # removed that ,("content_finders.intents_index",intent)
        
        #content_list[-1]['index']=next_index
        for index in range(len(content_list[-1])):
            content_list[-1][index]['index']=next_index
    content_list = flatten(content_list)
    return content_list

def fetch_keyboard(bot_id,index):

    """
    """
    
    keyboards = connection_wrapper(select_from_join,True,"content_finders","distinct on (content_finders.id) keyboards.name",
            (("bot_contents","content_finders.id","bot_contents.content_finders_id"),("contents","bot_contents.content_id","contents.id"),("keyboards","bot_contents.keyboard_id","keyboards.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("message_index",index)))
    return keyboards[0]['name']



from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from
import psycopg2
from functools import partial
import string
import random
import json
from utils import log

from exceptions.badinput import BadKeywordInputError
from exceptions.nopossibleanswer import NoPossibleAnswer


DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
GREETINGS = ['hi','hey', 'hello']

FEATURES_DICT_VOCAB = {"no":DEFAULT_NO,"yes":DEFAULT_YES,"dk":DEFAULT_DK}

def flatten(l):
    """
    Parameters:
        l (list) -- input list
    Returns:
        (list) -- output list flatten
    """
    return [item for sublist in l for item in sublist]

def find_keyword(input_str, word_list):
    """
    Loops through each word in the input string.
    Returns true is there is a match.

    Parameters:
        input_str (string) -- input string by the user
        word_list (list/tuple) -- list of extract_keywords_from_text

    Returns:
        (boolean) -- if keyword is found.
    """

    input_str = input_str.lower()
    return any([str(each) in str(input_str) for each in word_list])


def feature_selector_split(input_string,selector):
    """
    
    Take an input selector and parse it and 

    Parameters:
        input_str (string) -- input string by the user
        selector (string) -- an individual selector that will be parsed base on documentation rules see section selector.

    Returns:
        seletor (string) -- parsed selector 
        (boolean) -- if keyword is found.
    """

    log("[DEBUG]",f"Analysed selector is {selector}")
    try:
        if "?" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
            # these condition are formatted as ?keyword,alternative
            
            condition,alternative  = selector.split("?")
            
            word_list = FEATURES_DICT_VOCAB[condition]

            if (find_keyword(input_string,word_list) and (len(input_string.split(" ")) <= 5 and len(input_string) <= 25)): # the second condition is to make sure that the no is not contained in a long sentence
                #feature = selector.translate(str.maketrans('', '', string.punctuation)) # removing the punctuation from the selector that transforms it into a feature..,
                return condition,True
            else: 
                return alternative,True
        elif "!" in selector:
            selector = selector.replace("!","")
            return selector,True
        elif "none" in selector:
            return "none",True 
        
        elif "#" in selector or "@" in selector:
            return selector,False # we will process this selector after

    except BaseException as error:
            log('ERROR',f'Bad selector error due to {error}')

def selector_to_feature_or_trigger(selectors,input_string):

    features = []
    triggers = []

    for selector in selectors:
        selector,boolfeature = feature_selector_split(input_string,selector)
        if boolfeature:
            features.append(selector)
        elif not boolfeature:
            triggers.append(selector)
        else:
            pass

    if len(features) < 1: features.append('none') # sanity check to make sure that each index has a none
    return features,triggers

def fetch_selectors_name(message_index,bot_id):
    """
    Query the SQL database and return the features list associated with a particular bot_id 

    Parameters:
        msg_index (string) -- index of the particular message 
        bot_id (int) -- id of the current bot

    Returns:
        selectors (list/dict) --  
    """
    #we need to actualize the selectors to the lastest state
    selectors = connection_wrapper(select_from_join,True,"selector_finders","ALL selectors.name",
        (("selectors","selector_finders.selector_id","selectors.id"),),
        (("selector_finders.index",message_index),))
    return selectors

def fetch_feature_name(message_index,bot_id):
    #we need to actualize the selectors to the lastest state
    features = connection_wrapper(select_from_join,True,"feature_finders","ALL features.name",
        (("features","feature_finders.feature_id","features.id"),),
        (("feature_finders.index",message_index),))
    return features[0]

def find_index_in_feature_list(features,selectors):
    possible_indexes = set()
    for index,feature in enumerate(features):
        for selector in selectors:
            if set(feature)==set(selector):
                possible_indexes.add(index)
    return list(possible_indexes)

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
        content_list.append(connection_wrapper(select_from_join,True,"content_finders","content_finders.id,contents.text",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("bot_content_index",next_index)))[0]) # removed that ,("content_finders.features_index",feature)
        
        content_list[len(content_list)-1]['index']=next_index

    return content_list
    
def get_bot_response(bot_id,next_index,user_response,content_index):
    triggers = []
    
    next_indexes = fetch_next_indexes(bot_id,next_index) #for index in next_indexes]#1 fetching all the possible next index of the message for the given bot
    #next_indexes = list(set(flatten(next_indexes_list)))
    print(f'[DEBUG] Possible indexes are : {next_indexes}')
    next_contents = fetch_next_contents(bot_id,next_indexes) #2 fetching all the next possible content for the given bot
    print(f'[DEBUG] Possible contents are : {next_contents}')
    content_indexes = [content['id'] for content in next_contents] #3.1 getting all the possible feature from the current messages
    
    features_name = [fetch_feature_name(index,bot_id)['name'] for index in content_indexes] # 3.1.1 getting all the possible feature names
    selectors_name = [selector["name"] for selector in fetch_selectors_name(content_index,bot_id)]
    #selectors_name = [x.replace("?","") for x in selectors_name]
    log('DEBUG',f'Possible features are: {features_name}')
    log('DEBUG',f'Selectors are {selectors_name}')

    selected_feature,triggers = selector_to_feature_or_trigger(selectors=selectors_name,input_string=user_response)
    log("DEBUG",f'Selected features and triggers are : {selected_feature}, {triggers}')

    #selectors_name = [x.replace("?","").replace("!","").replace("#","") for x in selectors_name]
    
    possible_answers_index = find_index_in_feature_list(features=features_name,selectors=selected_feature) #4 matching the content index with the correct feature
    log('DEBUG',f'Possible indexes are { possible_answers_index}')
    possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the previous index, it might still be longer than 2 if we need to random between two messages
    
    #selectors_name = [x.replace("?","").replace("!","").replace("#","").replace("@","") for x in selectors_name]
    
    #if not bool(set(selectors_name).intersection(features_name)):
    #    log('ERROR','FATAL ERROR, script is wrong')

    if not bool(set(selected_feature).intersection(features_name)):#selected_feature not in features_name:len(set(features_name) - set(selected_feature)) > 1:
        raise BadKeywordInputError(features_name)
    elif len(possible_answers) < 1:
        raise BaseException


    print(f'[DEBUG] Possible answers are : {possible_answers}')

    if 'random' not in selected_feature and len(possible_answers)>1:
        print("Random is not in the feature space and there is mutiple responses") # add some variable to the log


    if len(possible_answers)>0:
        final_answers = possible_answers[random.randint(0,len(possible_answers)-1)]
        final_answers['next_indexes'] = final_answers['index']
         
    else:
        raise NoPossibleAnswer(bot_id,next_indexes)
        final_answers = {'text': "", 'next_indexes':next_indexes}
        print("[INFO] No available answer")



    return final_answers['text'],final_answers['next_indexes'],triggers



if __name__ == "__main__":
    

    bot_text = ""
    bot_id = 1
    next_index = 0
    

    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))




        


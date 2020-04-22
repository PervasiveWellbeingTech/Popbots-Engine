from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from
import psycopg2
from functools import partial
import string
import random
import json
from utils import log,timed

from exceptions.badinput import BadKeywordInputError
from exceptions.nopossibleanswer import NoPossibleAnswer
from exceptions.authoringerror import AuthoringError,NoMatchingSelectorPattern

from nltk.tokenize import word_tokenize



DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
GREETINGS = ['hi','hey', 'hello']
ENJOYABLE = ['enjoyable']
OTHER = ['other']
FEATURES_DICT_VOCAB = {"no":DEFAULT_NO,"yes":DEFAULT_YES,"dk":DEFAULT_DK,"greeting":GREETINGS,'enjoyable':ENJOYABLE,'other':OTHER}


def min_word(input_string,word_len,condition,alternative):
    
    if len(word_tokenize(input_string))>word_len:
        return condition,[condition,alternative]
    else:
        return alternative,[condition,alternative]

def greater_than(el1,el2,condition,alternative):
    
    if int(el1)>int(el2):
        return condition,[condition,alternative]
    else:
        return alternative,[condition,alternative]



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
        (boolean) -- true if keyword is found.
    """

    input_str = input_str.lower()
    return any([str(each) in str(input_str) for each in word_list])


def return_feature(input_string,condition,alternative):
    """
    Fetch the synonyms of the condition and return condition if input_string contains one the words or alternative. 
    """    
    word_list = FEATURES_DICT_VOCAB[condition]

    if (find_keyword(input_string,word_list) and (len(input_string.split(" ")) <= 5 and len(input_string) <= 25)): # the second condition is to make sure that the no is not contained in a long sentence
        feature = condition
    else: 
        feature = alternative
    return feature

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

    #log("DEBUG",f"Analysed selector is {selector}")

    parsed_features = []
    feature = None
    trigger = None
    print(selector)
    if "?" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
        # these condition are formatted as ?keyword,alternative
        features = selector.split("?")
        parsed_features = features.copy()

        alternative = features[-1]
        all_selectors = []
        del features[-1]

        for fea in features:

            all_selectors.append(return_feature(input_string,fea,alternative))
        
        feature_set = set(all_selectors) # sum all unique elements

        if len(feature_set)>1:
            if alternative in feature_set:
                feature_set.remove(alternative)
                if len(feature_set)>1:
                    feature_set = {alternative} # there is an ambiguity between two selectors folding back to else                
            else:
                feature_set = {alternative}
        
        feature = list(feature_set)[0]

    elif "@" in selector:

        if "@min_word" in selector:
            selector = selector.replace("@","")
            feature,temp_parsed_features = eval(selector)
            parsed_features = parsed_features + temp_parsed_features
        elif "@greater_than" in selector:
            selector = selector.replace("@","")
            feature,temp_parsed_features = eval(selector)
            parsed_features = parsed_features + temp_parsed_features

            
    elif "none" in selector:
        feature = "none"
        parsed_features.append(feature)
    elif "#" in selector or "!" in selector or "~" in selector or "tag:" in selector: ### these are triggers
        trigger = selector
    else:
        #log('ERROR','SELECTOR does not match any pattern error will be raised')
        raise BaseException
    
    return feature,trigger,parsed_features





def selector_to_feature_or_trigger(selectors,input_string):

    """

    Parameters:

    Returns:
    """

    features = []
    triggers = []
    possible_features = []

    for selector in selectors:
        feature,trigger,parsed_features = feature_selector_split(input_string,selector)
        
        if feature is not None: features.append(feature)
        elif trigger is not None: triggers.append(trigger)
        else:
            log('ERROR','No feature nor trigger has been extracted, the error should have happened before')

        possible_features += parsed_features 

    return features,triggers,possible_features

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

def fetch_triggers_name(message_index,bot_id):
    """
    Query the SQL database and return the trigger list associated with a particular bot_id at a certain index

    Parameters:
        msg_index (string) -- index of the particular message 
        bot_id (int) -- id of the current bot

    Returns:
        triggers (list/dict) --  
    """
    #we need to actualize the triggers to the lastest state
    triggers = connection_wrapper(select_from_join,True,"trigger_finders","ALL triggers.name",
        (("triggers","trigger_finders.trigger_id","triggers.id"),),
        (("trigger_finders.index",message_index),))
    return triggers

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
        content_list.append(connection_wrapper(select_from_join,True,"content_finders","distinct on (content_finders.id) content_finders.id,contents.text,keyboards.name",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id"),("keyboards","bot_contents.keyboard_id","keyboards.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("bot_content_index",next_index)))) # removed that ,("content_finders.features_index",feature)
        
        #content_list[-1]['index']=next_index
        for index in range(len(content_list[-1])):
            content_list[-1][index]['index']=next_index
    content_list = flatten(content_list)
    return content_list

@timed 
def get_bot_response(bot_user,next_index,user_response,content_index,stressor_object):
    global stressor

    bot_id = bot_user.id
    stressor = stressor_object
    next_indexes = fetch_next_indexes(bot_id,next_index) #for index in next_indexes]#1 fetching all the possible next index of the message for the given bot
    
    if len(next_indexes)<1:raise AuthoringError(bot_user.name,next_index,"no next index in next_message_finder")
    log('DEBUG',f'Possible indexes are : {next_indexes}')
    
    next_contents = fetch_next_contents(bot_id,next_indexes) #2 fetching all the next possible content for the given bot
    
    log('DEBUG',f'Possible contents are : {next_contents}')
    content_indexes = [content['id'] for content in next_contents] #3.1 getting all the possible feature from the current messages
    
    features_name = [fetch_feature_name(index,bot_id)['name'] for index in content_indexes] #3.1.1 getting all the possible feature names
    selectors_name = [selector["name"] for selector in fetch_selectors_name(content_index,bot_id)]
    
    try:selected_feature,triggers,parsed_features= selector_to_feature_or_trigger(selectors=selectors_name,input_string=user_response)
    except NoMatchingSelectorPattern as e:raise AuthoringError(bot_user.name,next_index,"bad selector pattern") from e
    
    log('DEBUG',f'Possible features are: {features_name}')
    log('DEBUG',f'All possible feature from selectors are {parsed_features}')
    log('DEBUG',f'Selectors are {selectors_name}')
    log("DEBUG",f'Selected features and triggers are : {selected_feature}, {triggers}')

    
    possible_answers_index = find_index_in_feature_list(features=features_name,selectors=selected_feature) #4 matching the content index with the correct feature
    log('DEBUG',f'Possible indexes are { possible_answers_index}')
    
    possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the previous index, it might still be longer than 2 if we need to random between two messages
    
    
    if not bool(set(parsed_features).intersection(features_name)):
        raise AuthoringError(bot_user.name,next_index,f"Selector to feature mismatch. Possible feature from selector: {' and '.join(set(parsed_features))} , but features given at next index is: {' and '.join(features_name)}")

    if not bool(set(selected_feature).intersection(features_name)):#selected_feature not in features_name:len(set(features_name) - set(selected_feature)) > 1:
        raise BadKeywordInputError(features_name)
    
    # user error or script 

    elif len(possible_answers) < 1:
        raise NoPossibleAnswer(bot_id,next_indexes)


    log('DEBUG',f'Possible answers are : {possible_answers}')

    if 'random!' not in triggers and len(possible_answers)>1:
        raise AuthoringError(bot_user.name,next_index,"Multiple responses and random is not in the feature space")
        
    if len(possible_answers)>0:
        final_answers = possible_answers[random.randint(0,len(possible_answers)-1)]
        final_answers['next_indexes'] = final_answers['index']
         
    else:
        raise NoPossibleAnswer(bot_id,next_indexes)
    
    message_local_trigger = [trigger['name'] for trigger in fetch_triggers_name(message_index=final_answers['id'],bot_id=bot_id)] 
    triggers += message_local_trigger # concatening triggers coming from the previous message selector and the new message "triggers". 

    return final_answers['text'],final_answers['next_indexes'],final_answers['name'],triggers



if __name__ == "__main__":
    
    """
    bot_text = ""
    bot_id = 1
    next_index = 0
    

    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,keyboard,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,content_index=59)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))
    """
    



        


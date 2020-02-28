from database_operations import connection_wrapper,insert_into,select_from_join,select_from
import psycopg2
from functools import partial
import string
import random
import json
from utils import log

DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
GREETINGS = ['hi','hey', 'hello']
DEFAULT_OTHERS = "__OTHERS__"

FEATURES_DICT_VOCAB = {"no?":DEFAULT_NO,"yes?":DEFAULT_YES,"idk?":DEFAULT_DK}

def flatten(a):
    return [item for sublist in a for item in sublist]

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


def validate_feature(input_string,selector):
    if "?" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
        word_list = FEATURES_DICT_VOCAB[selector]
        if (find_keyword(input_string,word_list) and (len(input_string.split(" ")) <= 5 and len(input_string) <= 25)): # the second condition is to make sure that the no is not contained in a long sentence
            feature = selector.translate(str.maketrans('', '', string.punctuation)) # removing the punctuation from the selector that transforms it into a feature..,
            return feature
        else: return "else"
    elif(selector == "random"):
        return "random"
    elif(selector == "else"):
        return "else"
    else:
        return "none"

def feature_selector_split(input_string,selector):
    log("[DEBUG]",f"Analysed selector is {selector}")
    try:
        if "?" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
            # these condition are formatted as ?keyword,alternative
            selector = selector.replace("?","")
            condition,alternative  = selector.split(",")
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
            log('ERROR','BAD SELECTOR')

def selector_to_feature_or_trigger(input_string,selector_index):

    selectors = fetch_selectors_name(selector_index)
    features = []
    triggers = []

    for selector in selectors:
        log('DEBUG',f"Features are {features}")
        selector,boolfeature = feature_selector_split(input_string,selector)
        if boolfeature:
            features.append(selector)
        elif not boolfeature:
            triggers.append(selector)
        else:
            pass

    if len(features) < 1: features.append('none') # sanity check to make sure that each index has a none
    return features,triggers

def fetch_selectors_name(selector_index):
    #we need to actualize the selectors to the lastest state
    selectors = connection_wrapper(select_from_join,False,"selector_finders","selectors.name",
        (("selectors","selector_finders.selector_id","selectors.id"),),
        (("selector_finders.index",selector_index),))
    return [selector[0] for selector in selectors]

def fetch_feature_name(feature_index):
    #we need to actualize the selectors to the lastest state
    features = connection_wrapper(select_from_join,True,"feature_finders","ALL features.name",
        (("features","feature_finders.feature_id","features.id"),),
        (("feature_finders.index",feature_index),))
    return features[0]

def selector_to_feature(input_string,selector_index):
    selectors = fetch_selectors_name(selector_index)
    feature_list = [validate_feature(input_string,selector) for selector in selectors]
    
    if len(feature_list) < 1: feature_list.append(['none']) # sanity check to make sure that each index has a none
    
    return feature_list


def features_to_indexes(input_string,selector_index):
    features = selector_to_feature(input_string,selector_index)
    return features


def fetch_next_indexes(bot_id,index):
    next_indexes = [index[0] for index in connection_wrapper(select_from,False,"next_message_finders","next_message_index",("user_id",bot_id),("source_message_index",index))]
    return next_indexes

def fetch_next_contents(bot_id,next_indexes):
    """
    Based on all the parameters this function queries the DB to get the current messages 
    Params that should not be forgotten include : language_id,language_type_id,

    """
    content_list=[]
    for next_index in next_indexes:
        content_list.append(connection_wrapper(select_from_join,True,"content_finders","contents.text,content_finders.selectors_index,content_finders.features_index",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("bot_content_index",next_index)))[0]) # removed that ,("content_finders.features_index",feature)
        content_list[len(content_list)-1]['index'] = next_index
    return content_list
    
def get_bot_response(bot_id,next_index,user_response,selector_index):
    triggers = []
    
    next_indexes = fetch_next_indexes(bot_id,next_index) #for index in next_indexes]#1 fetching all the possible next index of the message for the given bot
    #next_indexes = list(set(flatten(next_indexes_list)))
    print(f'[DEBUG] Possible indexes are : {next_indexes}')
    next_contents = fetch_next_contents(bot_id,next_indexes) #2 fetching all the next possible content for the given bot
    print(f'[DEBUG] Possible contents are : {next_contents}')
    features = [content['features_index'] for content in next_contents] #3.1 getting all the possible feature from the current messages
    features_name = [fetch_feature_name(feature_index)['name'] for feature_index in features] # 3.1.1 getting all the possible feature names
    
    log('DEBUG',f'The originally send selector is {selector_index}')

    if bot_id == 20: # test for onboarding bot

        selected_feature,triggers = selector_to_feature_or_trigger(user_response,selector_index)
        print(f'[DEBUG] Selected features and triggers are : {selected_feature}, {triggers}')

    else:
        selected_feature =[selector_to_feature(input_string=user_response,selector_index=selector_index)] #3.2 processing the message with the correct selector STILL Needs to iterate on features here
        print(f'[DEBUG] Possible features are: {features_name}')
        print(f'[DEBUG] Selected features are : {selected_feature}')
        selected_feature = selected_feature[0]
        
    possible_answers_index = [index for index,value in enumerate(features_name) if value in selected_feature] #4 matching the content index with the correct feature
    possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the previous index, it might still be longer than 2 if we need to random between two messages
    
    

                



    print(f'[DEBUG] Possible answers are : {possible_answers}')

    if 'random' not in selected_feature and len(possible_answers)>1:
        print("Random is not in the feature space and there is mutiple responses") # add some variable to the log


    if len(possible_answers)>0:
        final_answers = possible_answers[random.randint(0,len(possible_answers)-1)]
        final_answers['next_indexes'] = final_answers['index']
         
    else:
        final_answers = {'text': "", 'selectors_index': 1, 'features_index': 1,'next_indexes':next_indexes}
        print("[INFO] No available answer")



    return final_answers['text'],final_answers['next_indexes'],final_answers['features_index'],final_answers['selectors_index'],triggers



if __name__ == "__main__":
    

    bot_text = ""
    bot_id = 6
    next_index = 0
    selectors_index = 1 
    next_selector_index = 1 # default is always one
    conversation_index = 0
    conversation_id = 0

    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,features_index,selectors_index,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,selector_index=selectors_index)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))




        


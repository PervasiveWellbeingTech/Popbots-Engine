from database_operations import connection_wrapper,insert_into,select_from_join,select_from
import psycopg2
from functools import partial
import string
import random
import json


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
        if (find_keyword(input_string,word_list) or len(input_string.split(" ")) <= 5 and len(input_string) <= 25): # the second condition is to make sure that the no is not contained in a long sentence
            feature = selector.translate(str.maketrans('', '', string.punctuation)) # removing the punctuation from the selector that transforms it into a feature..,
            return feature
    elif(selector == "random"):
        return "random"
    elif(selector == "else"):
        return "else"
    else:
        return "none"
    






    

    
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
    content_list = [connection_wrapper(select_from_join,True,"content_finders","contents.text,content_finders.selectors_index,content_finders.features_index",
        (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id")),
        (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("bot_content_index",next_index)))[0] # removed that ,("content_finders.features_index",feature)
        for next_index in next_indexes]
    return content_list
    
def get_bot_response(bot_id,next_indexes,user_response,selector_index):

    next_indexes_list = [fetch_next_indexes(bot_id,index) for index in next_indexes]#1 fetching all the possible next index of the message for the given bot
    next_indexes = list(set(flatten(next_indexes_list)))
    print(f'Possible indexes are : {next_indexes} \n')
    next_contents = fetch_next_contents(bot_id,next_indexes) #2 fetching all the next possible content for the given bot
    print(f'Possible contents are : {next_contents} \n')
    features = [content['features_index'] for content in next_contents] #3.1 getting all the possible feature from the current messages
    features_name = [fetch_feature_name(feature_index)['name'] for feature_index in features] # 3.1.1 getting all the possible feature names
    print(f'Feature name is: {features_name}\n')
    selected_feature =[selector_to_feature(input_string=user_response,selector_index=selector_index)] #3.2 processing the message with the correct selector STILL Needs to iterate on features here
    print(f'Selected features are : {selected_feature}\n')
    possible_answers_index = [index for index,value in enumerate(features_name) if value in selected_feature[0]] #4 matching the content index with the correct feature
    
    possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the previous index, it might still be longer than 2 if we need to random between two messages
    print(f'Possible answers are : {possible_answers}\n')

    if 'random' not in selected_feature and len(possible_answers)>1:
        print("Random is not in the feature space and there is mutiple responses") # add some variable to the log


    if len(possible_answers)>0:
        final_answers = possible_answers[random.randint(0,len(possible_answers)-1)]
        final_answers['next_indexes'] = next_indexes
        
    else:
        final_answers = {'text': "", 'selectors_index': 1, 'features_index': 1,'next_indexes':next_indexes}
        print("No available answer")



        
    #text = '"' + next_contents[0]['text'].strip() + '"'


    return final_answers






if __name__ == "__main__":

    name="Thierry"
    bot_name="Johnny"
    problem="Not able to make it"


    user_response="Hi"
    selector_index = 1
    bot_id = 6
    response = {'text': "", 'selectors_index': None, 'features_index': None,"next_indexes":[0]}
    while response['text'] != "<CONVERSATION_END>":
        response = get_bot_response(bot_id=bot_id,next_indexes=response["next_indexes"],user_response=user_response,selector_index=selector_index)
        print(response['text'])
        selector_index = response['selectors_index']
        user_response = input()

        

        


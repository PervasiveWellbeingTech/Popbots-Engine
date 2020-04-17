#! ../popbots_venv/bin/python3

from controllers.main import *
from controllers.message import get_bot_response
from models.database_operations import connection_wrapper,select_from_join
from models.user import HumanUser,Users

from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest
session = ThreadSessionRequest().s

#user = thread_session.s.query(Users).filter_by(id=1231).delete()

#print(user)

"""
from controllers.main import dialog_flow_engine
from controllers.message import get_bot_response

  
if __name__ == "__main__":
    
    bot_text = ""
    bot_id = 1
    next_index = 0


    while bot_text != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_text,next_index,keyboards,triggers = get_bot_response(bot_id=bot_id,next_index=next_index,user_response=user_response,content_index=59)
        print("Bot reply: " + bot_text)
        print(" Next index is "+str(next_index))
    
 

    bot_response = ""
    while bot_response != "<CONVERSATION_END>":
        user_response = input("My  input: ")
        bot_response = dialog_flow_engine(user_id=1234567,user_message=user_response)
        print("Bot reply: " + str(bot_response['response_list']))
    """
DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
GREETINGS = ['hi','hey', 'hello']

FEATURES_DICT_VOCAB = {"no":DEFAULT_NO,"yes":DEFAULT_YES,"dk":DEFAULT_DK}

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


        
    elif "none" in selector:
        feature = "none"
        parsed_features.append(feature)
    elif "#" in selector or "@" in selector or "!" in selector: ### these are triggers
        trigger = selector
    else:
        #log('ERROR','SELECTOR does not match any pattern error will be raised')
        raise BaseException
    
    return feature,trigger,parsed_features




if __name__ == "__main__":
    #print(feature_selector_split("yes i am ready","no?else"))
    
    #list = ["~something","!random"]

    print(get_bot_ids(session,1,"Greeting Module"))
    
    #bool_trigger = [True if "~" in x else False for x in list ]
    #rint(not all(bool_trigger))



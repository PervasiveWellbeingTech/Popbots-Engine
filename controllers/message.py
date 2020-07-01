import psycopg2
import re
from functools import partial
import string
import random
import json
from utils import log,timed

from exceptions.badinput import BadKeywordInputError
from exceptions.nopossibleanswer import NoPossibleAnswer
from exceptions.authoringerror import AuthoringError,NoMatchingSelectorPattern
from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from,custom_sql
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent


from nltk.tokenize import word_tokenize



def stressor_pass(stressor):
    try:
        nb_of_stressor = connection_wrapper(custom_sql,True,f"SELECT count(id) FROM stressor s WHERE s.conversation_id ={stressor.conversation_id}")[0]['count']

        log("INFO",f"Number of stressor found is {nb_of_stressor}")
    except:
        nb_of_stressor = 0

    if nb_of_stressor > 1:
        return "yes",["yes","no"]
    else:
        return "no",["yes","no"]


def engagement(user):

    try:
        browsed_bots = [bot['name'] for bot in connection_wrapper(custom_sql,True,f"select distinct (u.name) from users u inner join messages m on m.sender_id =u.id where m.receiver_id = {user.user_id} and u.name like '%Bot';")]
        all_bots = [bot['name'] for bot in connection_wrapper(custom_sql,True,f"select distinct (u.name) from users u where u.name like '%Bot';")]

        inter = set(all_bots)-set(browsed_bots)

        log('INFO',f"user has interacted with {len(browsed_bots)} therefore he has {len(list(inter))} to explore ")
        if len(list(inter)) > 0:
            feature = "no"
        else:
            feature = "yes"

        
    except BaseException as error:
        log('ERROR',error)
        feature = "no"


    return feature,["yes","no"] 

def other_and_threshold(stressor):
    
    if stressor.category0.lower()=="other" or float(stressor.probability0)<0.2:
        feature = "other_or_threshold"

    elif False:
        feature = "none"
    
    else:
        feature = "yes"

    return feature,["yes","none","other_or_threshold"]

def two_cat_other(stressor):

    if stressor.probability0 - stressor.probability1 >0.2:
        feature = "yes" 
    else:
        if stressor.category1 == "Other":
            feature = "noother"
        else:
            feature = "two_possible"

    return feature,["yes","noother","two_possible"]


def min_word(input_string,word_len,condition,alternative):
    
    if len(word_tokenize(input_string))>word_len:
        return condition,[condition,alternative]
    else:
        return alternative,[condition,alternative]

def greater_than(el1,el2,condition,alternative):
    
    if float(el1)>float(el2):
        return condition,[condition,alternative]
    else:
        return alternative,[condition,alternative]
def is_number(input_string,condition,alternative):

    if input_string.isdecimal():
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
    word_list = [x.replace('"','').replace("\\","") for x in word_list]
    log('INFO',f"Trying to find > {word_list} < in the user string > {input_str}<" )

    return any([str(each).lower() in str(input_str)for each in word_list])

def fetch_synonyms_regex(feature_name):

    """
    """

    synonyms_regexes = connection_wrapper(select_from,True,"features","features.synonyms,features.regex",("features.name",feature_name),)
    synonyms = synonyms_regexes[0]['synonyms']
    regex = synonyms_regexes[0]['regex']

    synonyms = synonyms.split("|")
    
    return synonyms,regex





def return_feature(input_string,condition):
    """
    Fetch the synonyms of the condition and return condition if input_string contains one the words or alternative. 
    """    
    feature = None
    if "^" in condition:
        condition = condition.replace("^", "")

        if input_string == condition:
            feature = condition
    elif condition == "other" or condition=="else": # will always enter in those as general alternative 
            feature=condition
    else:

        synonyms,regex = fetch_synonyms_regex(condition.replace("'","''"))

        if regex is not None:
            regex = regex.replace(" ","") #replacing empty spaces in case
            if regex == "none":
                regex = 'a^'
        else:
            regex = 'a^'
        #and (len(input_string.split(" ")) <= 5 and len(input_string) <= 25)): # the second condition is to make sure that the no is not contained in a long sentence
       
        if find_keyword(input_string,synonyms) or re.match(rf"{regex}",input_string):
            feature = condition

    return feature

def feature_selector_split(selector,selector_kwargs):
    """
    
    Take an input selector and parse it and 

    Parameters:
        input_str (string) -- input string by the user
        selector (string) -- an individual selector that will be parsed base on documentation rules see section selector.

    Returns:
        seletor (string) -- parsed selector 
        (boolean) -- if keyword is found.
    """

    log("DEBUG",f"Analysed selector is {selector}")

    all_feature_from_selector = []
    feature = None
    trigger = None
    if "/" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
        # these condition are formatted as ?keyword,alternative
        alternative = "fallback"

        features = selector.split("/")
        all_feature_from_selector = features.copy()
        all_feature_from_selector.append(alternative)

        

        all_selectors = []
        for fea in features:
            all_selectors.append(return_feature(selector_kwargs['user_response'],fea))
        
        feature_set = set([x for x in all_selectors if x]) # take elements which as not "None" make a set to keep unique
        
        feature_no_systematic = list(feature_set - set(["else","other"]))


        if len(list(feature_set))>0:
                        
            if len(feature_no_systematic)>0:
                feature = feature_no_systematic[0]
            else:
                feature = "else" if "else" in list(feature_set) else "other"
        else:
            feature=alternative

    elif "@" in selector:
        print('Entered here')
        selector = selector.replace("@","")
        feature,temp_all_features = eval(selector)
        all_feature_from_selector = all_feature_from_selector + temp_all_features

    elif "none" in selector:
        feature = "none"
        all_feature_from_selector.append(feature)
    elif "#" in selector or "!" in selector or "~" in selector or "tag:" in selector: ### these are triggers
        trigger = selector
    else:
        #log('ERROR','SELECTOR does not match any pattern error will be raised')
        raise BaseException
    
    return feature,trigger,all_feature_from_selector





def selector_to_feature_or_trigger(selectors,selector_kwargs):

    """

    Parameters:

    Returns:
    """

    features = []
    triggers = []
    possible_features = []

    for selector in selectors:
        feature,trigger,all_feature_from_selector = feature_selector_split(selector,selector_kwargs)
        
        if feature is not None: features.append(feature)
        elif trigger is not None: triggers.append(trigger)
        else:
            log('ERROR','No feature nor trigger has been extracted, the error should have happened before')

        possible_features += all_feature_from_selector 

    

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

def fetch_keyboard(bot_id,index):
    
    keyboards = connection_wrapper(select_from_join,True,"content_finders","distinct on (content_finders.id) keyboards.name",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id"),("keyboards","bot_contents.keyboard_id","keyboards.id")),
            (("content_finders.user_id",bot_id),("contents.user_id",bot_id),("bot_content_index",index)))
    return keyboards[0]['name']




@timed 
def get_bot_response(session,bot_user,latest_bot_index,selector_kwargs):

    bot_id = bot_user.id
    content_finders = session.query(ContentFinders).filter_by(user_id=bot_id,message_index = latest_bot_index).first()

    selectors = [selector["name"] for selector in fetch_selectors_name(content_finders.id,bot_id)] # fetching the selectors from the previous message
    
    try:selected_feature,triggers,all_feature_from_selector= selector_to_feature_or_trigger(selectors=selectors,selector_kwargs=selector_kwargs)
    except NoMatchingSelectorPattern as e:raise AuthoringError(bot_user.name,latest_bot_index,"bad braching_options (selector) pattern ") from e

    
    if "fallback" in selected_feature:
        keyboard = fetch_keyboard(bot_id,latest_bot_index)

        final_answers = {"text":"Hmm... I\'m just a bot so I don\'t know how to respond to that here yet 🤔 \\n In the meantime, please use these buttons to respond",
                        "name":keyboard,"next_indexes":latest_bot_index}
    
    else:
    
        next_indexes = fetch_next_indexes(bot_id,latest_bot_index) #for index in next_indexes]#1 fetching all the possible next index of the message for the given bot
        
        if len(next_indexes)<1:raise AuthoringError(bot_user.name,latest_bot_index,"no next index provided")
        log('DEBUG',f'Possible indexes are : {next_indexes}')
        
        next_contents = fetch_next_contents(bot_id,next_indexes) #2 fetching all the next possible content for the given bot returns a dict
        
        log('DEBUG',f'Possible contents are : {next_contents}')
        content_indexes = [content['id'] for content in next_contents] # 2.0 putting all the indexes in a list
        
        #3.1 getting all the possible feature from the current messages
        
        possible_features = [fetch_feature_name(index,bot_id)['name'] for index in content_indexes] #3.1.1 getting all the possible feature names
        

        log('DEBUG',f'Possible features are: {possible_features}')
        log('DEBUG',f'All possible feature from selectors are {all_feature_from_selector}')
        log('DEBUG',f'Selectors are {selectors}')
        log("DEBUG",f'Selected features and triggers are : {selected_feature}, {triggers}')

        
        possible_answers_index = find_index_in_feature_list(features=possible_features,selectors=selected_feature) #4 matching the content index with the correct feature
        log('DEBUG',f'Possible indexes are { possible_answers_index}')
        
        possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the selected index, it might still be longer than 2 if we need to random between two messages
        
        
        if not bool(set(all_feature_from_selector).intersection(possible_features)):
            raise AuthoringError(bot_user.name,latest_bot_index,f"branching_options to incoming_branch_option mismatch. Possible incoming_branch_option from branching_options is/are: {' and '.join(set(all_feature_from_selector))} , but incoming_branch_option given at next index is/are: {' and '.join(possible_features)}")

        #if not bool(set(selected_feature).intersection(possible_features)):#selected_feature not in possible_features:len(set(possible_features) - set(selected_feature)) > 1:
        #    raise BadKeywordInputError(possible_features)
        
        # user error or script 

        elif len(possible_answers) < 1:
            raise NoPossibleAnswer(bot_id,next_indexes)


        log('DEBUG',f'Possible answers are : {possible_answers}')

        if 'random!' not in triggers and len(possible_answers)>1:
            raise AuthoringError(bot_user.name,latest_bot_index,"Multiple responses and random is not in the previous branching options (selector)")
            
        if len(possible_answers)>0:
            final_answers = possible_answers[random.randint(0,len(possible_answers)-1)]
            final_answers['next_indexes'] = final_answers['index']
            
        else:
            raise NoPossibleAnswer(bot_id,next_indexes)
        
        message_local_trigger = [trigger['name'] for trigger in fetch_triggers_name(message_index=final_answers['id'],bot_id=bot_id)] 
        triggers += message_local_trigger # concatening triggers coming from the previous message selector and the new message "triggers". 

    return final_answers['text'],final_answers['next_indexes'],final_answers['name'],triggers



    



        


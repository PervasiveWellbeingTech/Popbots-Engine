import re
import psycopg2
import string
import random
import json
from utils import log,timed,flatten
from functools import partial


from exceptions.badinput import BadKeywordInputError
from exceptions.nopossibleanswer import NoPossibleAnswer
from exceptions.authoringerror import AuthoringError,NoMatchingSelectorPattern
from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from,custom_sql
from models.conversation import Conversation,Message,Content,ContentFinders,MessageContent
from models.message import fetch_intent_name,fetch_keyboard,fetch_next_contents,fetch_next_indexes,fetch_selectors_name,fetch_synonyms_regex,fetch_triggers_name

from controllers.custom_intent_branching import * # all the custom intent/branching selector options these are performed with "eval"
from controllers.rasa_nlu import check_existence, load_all_models, return_rasa_prediction


load_all_models() # load all possible rasa models in memory

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




def return_intent(input_string,condition):
    """
    Fetch the synonyms of the condition and return condition if input_string contains one the words or alternative. 
    """    
    intent = None
    if "^" in condition:
        condition = condition.replace("^", "")

        if input_string == condition:
            intent = condition
    elif condition == "other" or condition=="else": # will always enter in those as general alternative 
            intent=condition
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
            intent = condition

    return intent

def intent_selector_split(selector,selector_kwargs):
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

    all_intent_from_selector = []
    intent = None

    if "/" in selector: # this is for the selectors where we need to check if the sentence is containing the word or the concept applies eg:negation
        # these condition are formatted as ?keyword,alternative
        alternative = "fallback"

        intents = selector.split("/")
        all_intent_from_selector = intents.copy()
        all_intent_from_selector.append(alternative)

        rasa_model = check_existence(intents)   
        if rasa_model: # a rasa model exists to do the splitting
            
            intent = return_rasa_prediction(rasa_model[0],selector_kwargs['user_response'])
        else:
            all_selectors = []
            for fea in intents:
                all_selectors.append(return_intent(selector_kwargs['user_response'],fea))
            
            intent_set = set([x for x in all_selectors if x]) # take elements which as not "None" make a set to keep unique
            
            intent_no_systematic = list(intent_set - set(["else","other"]))


            if len(list(intent_set))>0:
                            
                if len(intent_no_systematic)>0:
                    intent = intent_no_systematic[0]
                else:
                    intent = "else" if "else" in list(intent_set) else "other"
            else:
                intent=alternative

    elif "@" in selector:

        selector = selector.replace("@","")
        intent,temp_all_intents = eval(selector)
        all_intent_from_selector = all_intent_from_selector + temp_all_intents

    elif "none" in selector:
        intent = "none"
        all_intent_from_selector.append(intent)
    
    else:
        log('ERROR','SELECTOR does not match any pattern error will be raised')
        raise BaseException
    
    return intent,all_intent_from_selector





def selectors_to_intents(selectors,selector_kwargs):

    """

    Parameters:

    Returns:
    """

    intents = []

    possible_intents = []

    for selector in selectors:
        intent,all_intent_from_selector = intent_selector_split(selector,selector_kwargs)
        
        if intent is not None: intents.append(intent)
       
        else:
            log('ERROR','No intent has been extracted, the error should have happened before')

        possible_intents += all_intent_from_selector 

    

    return intents,possible_intents

def find_index_in_intent_list(intents,selectors):
    """
    """

    possible_indexes = set()
    for index,intent in enumerate(intents):
        for selector in selectors:
            if set(intent)==set(selector):
                possible_indexes.add(index)
    return list(possible_indexes)


@timed 
def get_bot_response(session,bot_user,latest_bot_index,selector_kwargs):
    
    """
        Function which perform the next message retrieval based on the bot_id, the previous message index, all possible intent provided at that index. 

        The process is as follow: 

            1. Fetching the outbound_intents (selectors) at index x
            2. Fetching the possible next messages at index x with their linked intent
            3. Processing the user's message to extract the relevant intent from the possible intent list
            4. Among the possible next messages, pick the one which match the relevant intent

        In some case the number of fetched answer might be greater than one. In that case, a !ramdom trigger must be set at the previous message index. 



    """


    bot_id = bot_user.id
    content_finders = session.query(ContentFinders).filter_by(user_id=bot_id,message_index = latest_bot_index).first()

    selectors = [selector["name"] for selector in fetch_selectors_name(content_finders.id)] # fetching the selectors from the previous message
    
    triggers = [trigger["name"] for trigger in fetch_triggers_name(message_index=content_finders.id,outbound=True)] # these are the outbound trigger from the previous message
    
    try:selected_intent,all_intent_from_selector= selectors_to_intents(selectors=selectors,selector_kwargs=selector_kwargs)
    except NoMatchingSelectorPattern as e:raise AuthoringError(bot_user.name,latest_bot_index,"bad braching_options (selector) pattern ") from e

    
    if "fallback" in selected_intent:
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
        
        #3.1 getting all the possible intent from the current messages
        
        possible_intents = [fetch_intent_name(index)['name'] for index in content_indexes] #3.1.1 getting all the possible intent names
        

        log('DEBUG',f'Possible intents are: {possible_intents}')
        log('DEBUG',f'All possible intent from selectors are {all_intent_from_selector}')
        log('DEBUG',f'Selectors are {selectors}')
        log("DEBUG",f'Selected intents and triggers are : {selected_intent}, {triggers}')

        
        possible_answers_index = find_index_in_intent_list(intents=possible_intents,selectors=selected_intent) #4 matching the content index with the correct intent
        log('DEBUG',f'Possible indexes are { possible_answers_index}')
        
        possible_answers = [next_contents[index] for index in possible_answers_index] #4.1 getting the actual content from the selected index, it might still be longer than 2 if we need to random between two messages
        
        
        if not bool(set(all_intent_from_selector).intersection(possible_intents)):
            raise AuthoringError(bot_user.name,latest_bot_index,f"branching_options to incoming_branch_option mismatch. Possible incoming_branch_option from branching_options is/are: {' and '.join(set(all_intent_from_selector))} , but incoming_branch_option given at next index is/are: {' and '.join(possible_intents)}")

        #if not bool(set(selected_intent).intersection(possible_intents)):#selected_intent not in possible_intents:len(set(possible_intents) - set(selected_intent)) > 1:
        #    raise BadKeywordInputError(possible_intents)
        
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
        
        message_local_trigger = [trigger['name'] for trigger in fetch_triggers_name(message_index=final_answers['id'],outbound=False)] 
        triggers += message_local_trigger # concatening triggers coming from the previous message selector and the new message "triggers". 

    return final_answers['text'],final_answers['next_indexes'],final_answers['name'],triggers



    



        


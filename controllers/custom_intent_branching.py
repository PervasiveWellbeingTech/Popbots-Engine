#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from utils import log,timed
from nltk.tokenize import word_tokenize
from models.database_operations import connection_wrapper,insert_into,select_from_join,select_from,custom_sql




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


def stressor_no_repeat(stressor):
    try:
        query = connection_wrapper(custom_sql,True,f"SELECT s.category0 FROM stressor s WHERE s.conversation_id ={stressor.conversation_id}")
        print(f"query stressor is: {query}")
        categories = [x['category0'] for x in query]
        nb_of_stressor = len(categories)
        log("INFO",f"Number of stressor found is {nb_of_stressor}")
    except:
        nb_of_stressor = 0
        categories = []

    if nb_of_stressor > 1 and len(list(set(categories)))==1:
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
            intent = "no"
        else:
            intent = "yes"

        
    except BaseException as error:
        log('ERROR',error)
        intent = "no"


    return intent,["yes","no"] 

def other_and_threshold(stressor):
    
    if stressor.category0.lower()=="other" or float(stressor.probability0)<0.2:
        intent = "other_or_threshold"

    elif False:
        intent = "none"
    
    else:
        intent = "yes"

    return intent,["yes","none","other_or_threshold"]

def two_cat_other(stressor):

    if stressor.probability0 - stressor.probability1 >0.2:
        intent = "yes" 
    else:
        if stressor.category1 == "Other":
            intent = "noother"
        else:
            intent = "two_possible"

    return intent,["yes","noother","two_possible"]

def is_financial(stressor):
    if stressor.category0 == "financial issues":
        return 'yes',["yes","no"] 
    else:
        return 'no',["yes","no"] 
def is_covid(stressor):
    if stressor.covid_category == "covid":
        if stressor.covid_probability > 0.99:
            return 'yes',["yes","no"] 
        else: return 'no',["yes","no"] 
    else:
        return 'no',["yes","no"] 

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


from database_operations import connection_wrapper,insert_into,select_from_join,select_from
import psycopg2
from functools import partial
import string


DEFAULT_YES = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
DEFAULT_NO = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
DEFAULT_DK = ["dk", "dunno", "dno", "don't know", "idk"]
GREETINGS = ['hi','hey', 'hello']
DEFAULT_OTHERS = "__OTHERS__"

FEATURES_DICT_VOCAB = {"no?":DEFAULT_NO,"yes?":DEFAULT_YES,"idk?":DEFAULT_DK}

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
            return selector.translate(str.maketrans('', '', string.punctuation)) # removing the punctuation from the selector that transforms it into a feature..,
    elif(selector == "random"):
        return "random"
    else:
        return "none"
    





class Message:
    def __init__(self):
        self.index = 1
        self.bot_id = 6
        self.selector_index = 1
        self.feature = 1
        self.language = 1 # 1 is for english
        self.language_type = 1 # 1 is for formal
        self.keyboard = None
    
    def fetch_selectors_name(self):
        #we need to actualize the selectors to the lastest state
        selectors = connection_wrapper(select_from_join,"selector_finders","selectors.name",
            (("selectors","selector_finders.selector_id","selectors.id"),),
            (("selector_finders.index",self.selector_index),))
        return [selector[0] for selector in selectors]
    
    def selector_to_feature(self,input_string):
        selectors = self.fetch_selectors_name()
        feature_list = [validate_feature(input_string,selector) for selector in selectors]
        return feature_list

    def features_to_indexes(self,input_string):
        features = self.selector_to_feature(input_string)


    def fetch_next_indexes(self):
        next_indexes = [index[0] for index in connection_wrapper(select_from,"next_message_finders","next_message_index",("user_id",self.bot_id),("source_message_index",self.index))]
        return next_indexes
    
    def fetch_next_contents(self,next_indexes):

        """
        Based on all the parameters this function queries the DB to get the current messages 
        Params that should not be forgotten include : language_id,language_type_id,

        """
        content_list = [connection_wrapper(select_from_join,"content_finders","contents.text,content_finders.selectors_index,content_finders.features_index",
            (("bot_contents","content_finders.bot_content_index","bot_contents.index"),("contents","bot_contents.content_id","contents.id")),
            (("content_finders.user_id",self.bot_id),("contents.user_id",self.bot_id),("bot_content_index",next_index),("content_finders.features_index",self.feature)))
            for next_index in next_indexes]
        return [{"text":text,"features_index":features_index,"selectors_index":selectors_index} for text,selectors_index,features_index in content_list]
        
    
if __name__ == "__main__":

    a = Message()
    b = a.fetch_next_indexes()
    c = a.fetch_next_contents(b) #[0][0][0].strip().format(name="Thierry",bot_name="Johnny",problem="Not able to make it"))
    #print(a.selector_to_feature(input_string="no i don't want to do this"))
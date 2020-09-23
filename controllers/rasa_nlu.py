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

import os
import json
from itertools import permutations


"""
Doc for this python rasa api is here https://legacy-docs.rasa.com/docs/nlu/0.15.1/python/

"""

from rasa.nlu.training_data import load_data
from rasa.nlu.model import Trainer
from rasa.nlu import config
from rasa.nlu.model import Interpreter
from rasa.nlu.components import ComponentBuilder
from rasa.nlu.components import Component


builder = ComponentBuilder(use_cache=True)      # will cache components between pipelines (where possible)
#config = RasaNLUConfig("sample_configs/config_spacy.json")


# functions related to model training


def intent_dict(intent,text):
    return {
          "text": text,
          "intent": intent,
          "entities": []
        }

def convert_to_rasa_json(intents):
    """

    """

    rasa_dict = {
        "rasa_nlu_data":{"regex_features": [],"entity_synonyms": [],"common_examples":[]}
    }

    for intent, intent_synonyms in intents:
        for synonyms in intent_synonyms:
            rasa_dict["rasa_nlu_data"]["common_examples"].append(intent_dict(intent=intent,text=synonyms))


    return rasa_dict


MODEL_PATH = './rasa_data/projects/default/'
DATA_PATH = './rasa_data/data/'


def train_rasa_model(selector_name,intents):

    file = open(DATA_PATH+'examples/rasa/'+selector_name+'.json','w')
    file.writelines(json.dumps(convert_to_rasa_json(intents), indent=4))
    file.close()


    training_data = load_data(DATA_PATH+'examples/rasa/'+selector_name +'.json')
    trainer = Trainer(config.load(DATA_PATH+"test_config/diet_spacy.yml"),builder)
    trainer.train(training_data)
    model_directory = trainer.persist(MODEL_PATH, fixed_model_name=selector_name)  # Returns the directory the model is stored in



def load_all_models():
    all_models = os.listdir(MODEL_PATH)

    for model in all_models:
        try:
            globals()[model] = Interpreter.load(MODEL_PATH+model,builder)
        except BaseException as error:
            print(f"Could not load model {model} error with {error}")


def check_existence(intent_list):

    all_models = os.listdir(MODEL_PATH)
    permutation = ["_".join(a) for a in permutations(intent_list, len(intent_list))]

    intersection = list(set(all_models) & set(permutation))

    return intersection
   


def return_rasa_prediction(model_name,input_text):
    
    prediction = globals()[model_name].parse(input_text)
    return prediction['intent']['name']




import os
import traceback
import pickle
import datetime
import pytz
import pandas 
from time import sleep
from models.qualtrics import return_survey_csv

from utils import logger



to_upload_df = pandas.DataFrame()
presurvey_id = 'SV_cTOc1Nhjbf1PLlX'

TEMP_QUALTRICS_DATA = "qualtrics_survey/PopBots July 2020 Pilot - Pre-Study Survey.csv"

columns = pandas.read_csv("../columns_name_pre.csv",header=None)[0].tolist()
n=3
columns_chunks = [columns[i:i + n] for i in range(0, len(columns), n)]


#columns_chunks = [['BIG5_1', 'Q31_1', 'I see myself as someone who ... - ... is reserved'], ['BIG5_2', 'Q31_2', 'I see myself as someone who ... - ... is generally trusting'], ['BIG5_3', 'Q31_3', 'I see myself as someone who ... - ... tends to be lazy'], ['BIG5_4', 'Q31_4', 'I see myself as someone who ... - ... is relaxed, handles stress well'], ['BIG5_5', 'Q31_5', 'I see myself as someone who ... - ... has few artistic interests'], ['BIG5_6', 'Q31_6', 'I see myself as someone who ... - ... is outgoing, sociable'], ['BIG5_7', 'Q31_7', 'I see myself as someone who ... - ... tends to find fault with others'], ['BIG5_8', 'Q31_8', 'I see myself as someone who ... - ... does a thorough job'], ['BIG5_9', 'Q31_9', 'I see myself as someone who ... - ... gets nervous easily'], ['BIG5_10', 'Q31_10', 'I see myself as someone who ... - ... has an active imagination'], ['Age', 'Q5', 'What is your age?'], ['Education', 'Q18', 'What is the highest degree or level of school you have completed?'], ['Employment', 'Q20', 'What is your current employment status?'], ['Industry', 'Q22', 'Which option best describes the industry you primarily work in? - Selected Choice'], ['marital_status', 'Q24', 'Which of the following best describes your marital status?'], ['nb_childrens', 'Q26', 'How many children do you have?'], ['household_income', 'Q28', 'What is your current household income? (USD)'], ['social_media', 'Q30', 'How much time do you spend on social media per day?'], ['Gender', 'Q58', 'Which of the following best describes your gender identity?'], ['daily_stress_assesment', 'Q3', 'How much stress do you feel on a daily basis?']]
big_5_column_dict = {}
phq4_column_dict = {}
for el in columns_chunks:
    if 'BIG' in el[0]:
        big_5_column_dict[el[0]] = el[1]
    elif "phq" in el[0]:
        phq4_column_dict[el[0]] = el[1]
all_columns = {}
for el in columns_chunks:
    all_columns[el[0]] = el[1]



print(big_5_column_dict)


big_5_short = {"Strongly Disagree":1, "Disagree":2, "Neither Agree nor Disagree":3,"Agree":4,"Strongly Agree":5}
phq_4_short = {"Not at All":0, "Several Days":1, "More than Half the Days":2,"Nearly Every Day":4}


#return_survey_csv(logger,presurvey_id)

surveys = pandas.read_csv(TEMP_QUALTRICS_DATA)
surveys = surveys.loc[2:]
surveys = surveys[surveys['Finished']=='True'] # only consider surveys which are completed
surveys = surveys.reset_index()
surveys.replace('\n',' ', inplace=True,regex=True)

print(surveys[big_5_column_dict.values()].head(10))

big_5 = ["extraversion","agreeableness","conscientiousness","neuroticism","openness"]


for personality in big_5:
    to_upload_df.loc[:,"is_"+personality] = [0]*len(surveys)


for index,response in surveys.iterrows():
    try:
        extraversion = (5 - int(big_5_short[response[big_5_column_dict['BIG5_1']]])) + int(big_5_short[response[big_5_column_dict['BIG5_6']]])
        agreeableness = (5 - int(big_5_short[response[big_5_column_dict['BIG5_7']]])) + int(big_5_short[response[big_5_column_dict['BIG5_2']]])
        conscientiousness = (5 - int(big_5_short[response[big_5_column_dict['BIG5_3']]])) + int(big_5_short[response[big_5_column_dict['BIG5_8']]])
        neuroticism = (5 - int(big_5_short[response[big_5_column_dict['BIG5_4']]])) + int(big_5_short[response[big_5_column_dict['BIG5_9']]])
        openness = (5 - int(big_5_short[response[big_5_column_dict['BIG5_5']]])) + int(big_5_short[response[big_5_column_dict['BIG5_10']]])

        phq4 = int(phq_4_short[response[phq4_column_dict['phq4_1']]]) + int(phq_4_short[response[phq4_column_dict['phq4_2']]]) + int(phq_4_short[response[phq4_column_dict['phq4_3']]]) + int(phq_4_short[response[phq4_column_dict['phq4_4']]])


        participant_big_5_num_list = [extraversion,agreeableness,conscientiousness,neuroticism,openness]
        m = max(participant_big_5_num_list)

        participant_big_5_list = [big_5[i] for i, j in enumerate(participant_big_5_num_list) if j == m]

        for personality in participant_big_5_list:
            to_upload_df.loc[index,"is_"+personality] = 1
        to_upload_df.loc[index,"phq4"] = phq4

        for key,value in all_columns.items():
            to_upload_df.loc[index,key] = surveys.loc[index,value]
        
    except BaseException as Error:
        print(response['Q20'])
        print(Error)

    


# only take data from row 2 
#surveys = surveys[surveys['Q1'] == "I agree."]


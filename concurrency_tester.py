from multiprocessing import Process, Pool
import random
import time
import datetime
import numpy as np
import sys
from controllers.main import dialog_flow_engine
from models.user import HumanUser,Users 
from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest
thread_session = ThreadSessionRequest()
NUM_USERS=1
INTRA_MSG_SLEEP = 5 # in seconds
res_report = None
all_hi_avgs = []
all_conv_avgs = []

messages = ["Yes","The amount of shifts I have to cover at work due to people calling out.","Yeah", "I do 13h shifts"]
NUM_MESSAGES = len(messages)#5 # Excluding initial 'Hi' message
def add_user(session,user_id):
    #delete = thread_session.s.query(Users).filter_by(id=user_id).delete()
    user = HumanUser(user_id=user_id)
    user.subject_id = 123 #re.findall(' ([0-9]+)', user_message)
    user.language_id = 1 # for english
    user.language_type_id = 1 # for formal
    user.category_id = 1
    user.name = "Test Concurrency " + str(user_id) # this is the default
    ### Redirect response of session to keep console clear
    save_stdout = sys.stdout
    sys.stdout = open("ConversationLogs2", "w+")
    session.add(user)
    session.commit()
    sys.stdout = save_stdout
def user(user_id):
    session = thread_session.s
    user = session.query(Users).filter_by(id=user_id).first()
    if user is None:
        res_report.write("Entered in user with id: " + str(user_id) + '\n')
        add_user(session,user_id)
    initTimes = []
    # Start conversation with a "Hi"
    start = time.time()
    ### Redirect response of dialog_flow_engine to keep console clear
    save_stdout = sys.stdout
    sys.stdout = open("ConversationLogs", "w+")
    response = dialog_flow_engine(user_id, "Hi")
    sys.stdout = save_stdout
    ###
    end = time.time()
    t = end - start
    print("USER: ", user_id, " TIME:", t)
    initTimes.append(t)
    time.sleep(INTRA_MSG_SLEEP)
    # Continue conversation by sending simple message
    convTimes = []
    for i in range(NUM_MESSAGES):
        start = time.time()
        response = dialog_flow_engine(user_id, messages[i])
        end = time.time()
        t = end-start
        print("USER: ", user_id, " TIME:", t)
        convTimes.append(t)
        time.sleep(INTRA_MSG_SLEEP)
    initTimes = np.array(initTimes)
    convTimes = np.array(convTimes)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(initTimes, initTimes.mean())
    print(convTimes, convTimes.mean())
    return [initTimes.mean(),convTimes.mean(),"Aggregate User "+ str(user_id) + " Max " + str(convTimes.max()) + " Min " + str(convTimes.min()) + " Avg "+ str(convTimes.mean())]
if __name__ == '__main__':
    res_report = open("concurrency_test_results.txt", "a+")
    res_report.write("\n\n=================New Report====================\n")
    res_report.write("Date: " + str(datetime.datetime.now()) + '\n')
    NUM_USERS = int(input("Number of simultaneous users: "))
    res_report.write("Num Users Generated: " + str(NUM_USERS) + '\n')
    #NUM_MESSAGES = int(input("Number of messages sent per user (excluding initial Hi): "))
    res_report.write("Msgs per user (excluding initial \'Hi\'): " + str(NUM_MESSAGES) + '\n')
    #all_hi_avgs = []
    #all_conv_avgs = []
    p = Pool(NUM_USERS)
    users = [int("123"+str(x)) for x in range(NUM_USERS)]
    output = p.map(user, users)
    for o in output:
        #print(o[2])
        all_hi_avgs.append(o[0])
        all_conv_avgs.append(o[1])
        res_report.write(str(o))
    all_hi_avgs = np.array(all_hi_avgs)
    all_conv_avgs = np.array(all_conv_avgs)
    print("=============Total avg times for " + str(NUM_USERS) + " generated conversations=====================")
    #print(all_hi_avgs)
    #print(all_conv_avgs)
    res_report.write("Average time to receive response to \"Hi\": " + str(all_hi_avgs.mean())  + '\n')
    res_report.write("Average time to receive response in conversation: " + str(all_conv_avgs.mean()) + '\n')
    res_report.write("\n\n=================End Report====================")
    res_report.write("============================================")
    res_report.close()
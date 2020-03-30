from multiprocessing import Process, Pool
import random
import time
import numpy as np

from controllers.main import dialog_flow_engine

from models.user import HumanUser,Users

from models.core.sqlalchemy_config import get_session,get_base,ThreadSessionRequest
thread_session = ThreadSessionRequest()

NUM_USERS = 20
NUM_MESSAGES = 1



def add_user(user_id):
    delete = thread_session.s.query(Users).filter_by(id=user_id).delete()
    session = thread_session.s
    user = HumanUser(user_id=user_id)
    user.subject_id = 123 #re.findall(' ([0-9]+)', user_message)
    user.language_id = 1 # for english
    user.language_type_id = 1 # for formal 
    user.category_id = 1
    
    user.name = "Test Concurrency " + str(user_id) # this is the default
    session.add(user)
    session.commit()

def user(user_id):

    #add_user(user_id)
    times = []
    for i in range(NUM_MESSAGES):
        start = time.time()
        response = dialog_flow_engine(user_id, "Hi")
        end = time.time() 
        t = end-start
        print("USER: ", user_id, " TIME:", end-start)
        times.append(t)
        time.sleep(random.random()+2)
    times = np.array(times)
    return "Aggregate User "+str(user_id)+" Max "+str(times.max())+" Min "+str(times.min())+ " Avg "+str(times.mean())




if __name__ == '__main__':
    p = Pool(NUM_USERS)

    users = [int("123"+str(x)) for x in range(NUM_USERS)]
    output = p.map(user, users)
    for o in output:
        print(o)

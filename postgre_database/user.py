from sqlalchemy import Table, Column, Integer, \
        String, MetaData, join, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property,sessionmaker

from sqlalchemy import create_engine

metadata = MetaData()
Base = declarative_base()
engine = create_engine('postgresql+psycopg2://popbots:popbotspostgres7@localhost/popbots')
Session = sessionmaker(bind=engine)
session = Session()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category_id = Column(Integer)
        

class HumanUsers(Base):
    __tablename__ = 'human_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    subject_id = Column(String)
    language_type_id = Column(Integer)
    language_id = Column(Integer)
        



human_users_join = join(Users,HumanUsers)


"""
class USER():
    def __init__(self,user_id,subject_id):
        self.id = user_id
        self.name = None
        self.choice = False
        self.formal = False
        self.switch = False
        self.suject_id = subject_id
        self.language_id = 1 # default is english with id 1
        self.language_type = 1 # default language type is formal 1 
        self.possible_response_ids = None
        self.current_bot_id = None
        self.conv_id = None
        self.last = None
        self.switch = None
        self.problem = []


"""
# map to it
class HumanUser(Base):
    __table__ = human_users_join

    user_id = column_property(Users.id, HumanUsers.user_id)
    human_users_id = HumanUsers.id
    name = Users.name

    subject_id = HumanUsers.subject_id
    language_id= HumanUsers.language_id
    language_type_id = HumanUsers.language_type_id




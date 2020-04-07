import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey, \
        create_engine, Column, Integer,Boolean, String,DateTime,ForeignKey,Float
from sqlalchemy.sql import func

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker,column_property,relationship
from sqlalchemy.ext.declarative import declarative_base
from models.core.config import config_string # this is the sqlalchemy formatted string

RUNNING_DEVSERVER = False

metadata = MetaData()


engine = create_engine(config_string())
session_factory = sessionmaker(bind=engine,autoflush=True)
Session = scoped_session(session_factory)

def get_session():
    return Session()
def get_base():
    return declarative_base()

class ThreadSessionRequest(object):
    def __init__(self): # , request, *args, **kwargs
        self.s = Session()

    
    def __del__(self):
        if self.s:
            self.remove_session()

    def remove_session(self):
        if self.s:
            try:
                self.safe_commit()
            finally:
                Session.remove()
                del self.s
                self.s = None

    def safe_commit(self):
        if self.s:
            try:
                self.s.commit()
            except:
                self.s.rollback()
                raise
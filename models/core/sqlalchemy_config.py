import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey, \
        create_engine, Column, Integer,Boolean, String,DateTime,ForeignKey

from sqlalchemy.orm import sessionmaker,column_property,relationship
from sqlalchemy.ext.declarative import declarative_base
from models.core.config import config_string # this is the sqlalchemy formatted string


metadata = MetaData()
engine = create_engine(config_string())
Session = sessionmaker(bind=engine)
session = Session()

def get_session():
    return Session()
def get_base():
    return declarative_base()


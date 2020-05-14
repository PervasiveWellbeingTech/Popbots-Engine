import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey, \
        create_engine, Column, Integer,Boolean, String,DateTime,ForeignKey,Float
from sqlalchemy.sql import func

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker,column_property,relationship
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from models.core.config import config_string # this is the sqlalchemy formatted string

from utils import log,timed



from sqlalchemy.exc import OperationalError, StatementError,InvalidRequestError
from psycopg2.errors import AdminShutdown,IdleInTransactionSessionTimeout
from sqlalchemy.orm.query import Query as _Query
from time import sleep

class RetryingQuery(_Query):
    __max_retry_count__ = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return super().__iter__()
            except (OperationalError,IdleInTransactionSessionTimeout,AdminShutdown) as ex:
                if "server closed the connection unexpectedly" not in str(ex):
                    raise
                if attempts <= self.__max_retry_count__:
                    sleep_for = 2 ** (attempts - 1)
                    log('ERROR',
                        "/!\ Database connection error: retrying Strategy => sleeping for {}s"
                        " and will retry (attempt #{} of {}) \n Detailed query impacted: {}".format(
                            sleep_for, attempts, self.__max_retry_count__, ex))
                    sleep(sleep_for)
                    continue
                else:
                    raise
            except (StatementError,InvalidRequestError) as ex:
                if "reconnect until invalid transaction is rolled back" not in str(ex):
                    raise
                log('ERROR',str(ex))
                self.session.rollback()

RUNNING_DEVSERVER = False

metadata = MetaData()


engine = create_engine(config_string(),pool_size=20,pool_pre_ping=True,pool_recycle=300,pool_timeout=1800)
session_factory = sessionmaker(bind=engine,query_cls=RetryingQuery,autoflush=True)
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
            log("INFO","Safely removing session")
            self.remove_session()

    def remove_session(self):
        if self.s:
            try:
                self.safe_commit()
            finally:
                self.s.close()
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
from models.core.sqlalchemy_config import * #delete all the above and see if it works
session = get_session()
Base = get_base()

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True) # auto incrementing
    logger = Column(String) # the name of the logger. (e.g. myapp.views)
    level = Column(String) # info, debug, or error?
    trace = Column(String) # the full traceback printout
    msg = Column(String) # any custom log you may have included
    created_at = Column(DateTime, default=func.now()) # the current timestamp

    def __init__(self, logger=None, level=None, trace=None, msg=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])
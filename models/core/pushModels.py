
from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.user import Users
import traceback
import pandas as pd


session = get_session()
Base = get_base()


class Keyboards(Base):
    __tablename__ = 'keyboards'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class LanguageTypes(Base):
    __tablename__ = 'language_types'
    id = Column(Integer, primary_key=True)
    name = Column(String)

"""
selector_finders_table = Table('selector_finders', Base.metadata,
    Column('id',Integer,primary_key=True),
    Column('index', Integer, ForeignKey('content_finders.id')),
    Column('selectors_id', Integer, ForeignKey('selectors.id'))
)
"""


class Selectors(Base):
    __tablename__='selectors'
    id = Column(Integer,primary_key=True)
    name = Column(String)


class SelectorFinders(Base):
    __tablename__='selector_finders'
    id = Column(Integer,primary_key=True)
    index =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    selector_id = Column(Integer, ForeignKey('selectors.id'))

class Intents(Base):
    __tablename__='intents'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    synonyms = Column(String)
    regex=Column(String)

class IntentFinders(Base):
    __tablename__='intent_finders'
    id = Column(Integer,primary_key=True)
    index =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    intent_id = Column(Integer, ForeignKey('intents.id'))

class Trigger(Base):
    __tablename__='triggers'
    id = Column(Integer,primary_key=True)
    name = Column(String)
    outbound = Column(Boolean)

class TriggerFinders(Base):
    __tablename__='trigger_finders'
    id = Column(Integer,primary_key=True)
    index =  Column(Integer, ForeignKey('trigger_finders.id', ondelete='CASCADE'))
    trigger_id = Column(Integer, ForeignKey('triggers.id'))


class ContentFinders(Base):
    __tablename__='content_finders'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    source_message_index = Column(Integer)
    message_index = Column(Integer)
    bot_content_index = Column(Integer)
    selectorFinders = relationship(SelectorFinders,cascade='all,delete',passive_deletes=True)
    intentFinders = relationship(IntentFinders,cascade='all,delete',passive_deletes=True)

    #intents_index = Column(Integer)
    #selectors_index = relationship("Selectors",secondary=selector_finders_table,backref='contents',lazy='dynamic')



#print(Base.metadata)
#Base.metadata.create_all(engine)


def push_selector_list(session,selectors,content_finder_id):

    try:

        for sel in selectors:
            selector = session.query(Selectors).filter_by(name=sel).first()

            if selector is None:
                selector = Selectors(name=sel)
                session.add(selector)
                session.commit()

            manytomany = SelectorFinders(index=content_finder_id,selector_id = selector.id)
            session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)

def push_intent_list(session,intents,content_finder_id,synonyms_regexes):

    synonyms_regexes['incoming_branch_option'] = synonyms_regexes['incoming_branch_option'].str.lower()

    try:

        for fea in intents:

            
            row = synonyms_regexes.loc[synonyms_regexes['incoming_branch_option'] ==fea,:] 
            if all(list(row.all().isnull().values)):
                raise Exception(f"No synonyms nor regex has been found for incoming_branching_options {fea}")
            else:

             
                if row.regex.values == 'none':
                    regex = None
                else:
                    regex = str(row.regex.values[0]).strip("'")

                if row.synonyms.values == 'none':
                    synonyms = None
                else:
                    synonyms = str(row.synonyms.values).strip("][").strip("'")

                if synonyms is None and regex is None and fea != 'none':
                    raise Exception(f"Synonyms and regex together are none for incoming_branching_options(ICO) {fea} this is not allowed, the synonym should at least contain (if applies) the name of the ICO itself")
                
                intent = session.query(Intents).filter_by(name=fea).first()

                if intent is None:
                    intent = Intents(name=fea,synonyms=synonyms,regex=regex)
                    session.add(intent)
                    session.commit()
                else:
                    intent.synonyms = synonyms
                    intent.regex = regex
                    session.commit()

                manytomany = IntentFinders(index=content_finder_id,intent_id = intent.id)
                session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)
        tb = traceback.TracebackException.from_exception(error)
        print(''.join(tb.stack.format()))

def push_trigger_list(session,triggers,content_finder_id):

    try:

        for trig,outbound in triggers:
            trigger = session.query(Trigger).filter_by(name=trig,outbound=outbound).first()

            if trigger is None:
                trigger = Trigger(name=trig,outbound=outbound)
                session.add(trigger)
                session.commit()

            manytomany = TriggerFinders(index=content_finder_id,trigger_id = trigger.id)
            session.add(manytomany)
        
        session.commit()

    except Exception as error:
        print(error)
        tb = traceback.TracebackException.from_exception(error)
        print(''.join(tb.stack.format()))



if __name__ == "__main__":
    push_intent_list(intents=["no!","yes!","proper!"],content_finder_id=2)




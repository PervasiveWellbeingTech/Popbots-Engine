
from models.core.sqlalchemy_config import * #delete all the above and see if it works
from models.user import Users


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

class Features(Base):
    __tablename__='features'
    id = Column(Integer,primary_key=True)
    name = Column(String)

class FeatureFinders(Base):
    __tablename__='feature_finders'
    id = Column(Integer,primary_key=True)
    index =  Column(Integer, ForeignKey('content_finders.id', ondelete='CASCADE'))
    feature_id = Column(Integer, ForeignKey('features.id'))


class ContentFinders(Base):
    __tablename__='content_finders'
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey(Users.id))
    source_message_index = Column(Integer)
    message_index = Column(Integer)
    bot_content_index = Column(Integer)
    selectorFinders = relationship(SelectorFinders,cascade='all,delete',passive_deletes=True)
    featureFinders = relationship(FeatureFinders,cascade='all,delete',passive_deletes=True)

    #features_index = Column(Integer)
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

    except exc.IntegrityError as error:
        print(error)

def push_feature_list(session,features,content_finder_id):

    try:

        for fea in features:
            feature = session.query(Features).filter_by(name=fea).first()

            if feature is None:
                feature = Features(name=fea)
                session.add(feature)
                session.commit()

            manytomany = FeatureFinders(index=content_finder_id,feature_id = feature.id)
            session.add(manytomany)
        
        session.commit()

    except exc.IntegrityError as error:
        print(error)


if __name__ == "__main__":
    push_feature_list(features=["no!","yes!","proper!"],content_finder_id=2)




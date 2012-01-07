from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Enum,
    Integer,
    Date,
    DateTime,
    Interval,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    password = Column(String)

    def __init__(self, email, name, password, babies=None):
        self.email = email
        self.name = name
        self.password = password

        if babies is None:
            babies = []
        self.babies = babies

class Baby(Base):
    __tablename__ = 'babies'

    id = Column(Integer, primary_key=True)
    dob = Column(Date)
    name = Column(String)
    gender = Column(Enum('m', 'f'))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('babies', order_by=id))

    def __init__(self, dob, name, gender, user):
        self.dob = dob
        self.name = name
        self.gender = gender
        self.user = user

class Entry(Base):
    __tablename__ = 'entries'


    id = Column(Integer, primary_key=True)
    type = Column(String)

    baby_id = Column(Integer, ForeignKey('babies.id'))
    baby = relationship("Baby")

    start = Column(DateTime)
    end = Column(DateTime, nullable=True)
    note = Column(String, nullable=True)

    __mapper_args__ = {'polymorphic_on': type}

    def __init__(self, baby, start, end=None, note=None):
        self.baby = baby
        self.start = start
        self.end = end
        self.note = note

class DurationEntry(Entry):
    duration = Column(Interval)

class AmountEntry(Entry):
    amount = Column(Integer)

class BreastFeed(DurationEntry):
    __mapper_args__ = {'polymorphic_identity': 'breastfeed'}

    def __init__(self, baby, start, duration, end=None, note=None):
        super(BreastFeed, self).__init__(baby, start, end, note)
        self.duration = duration

class BottleFeed(AmountEntry):
    __mapper_args__ = {'polymorphic_identity': 'bottlefeed'}

    def __init__(self, baby, start, amount, end=None, note=None):
        super(BottleFeed, self).__init__(baby, start, end, note)
        self.amount = amount

class MixedFeed(DurationEntry, AmountEntry):
    __mapper_args__ = {'polymorphic_identity': 'mixedfeed'}

    def __init__(self, baby, start, duration, amount, end=None, note=None):
        super(MixedFeed, self).__init__(baby, start, end, note)
        self.duration = duration
        self.amount = amount

class Sleep(DurationEntry):
    __mapper_args__ = {'polymorphic_identity': 'sleep'}

    def __init__(self, baby, start, duration, end=None, note=None):
        super(Sleep, self).__init__(baby, start, end, note)
        self.duration = duration

class Nappy(Entry):
    __mapper_args__ = {'polymorphic_identity': 'nappy'}

    contents = Column(Enum('wet', 'dirty'))

    def __init__(self, baby, start, contents, end=None, note=None):
        super(Nappy, self).__init__(baby, start, end, note)
        self.contents = contents

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Enum,
    Integer,
    Date,
    DateTime,
    Time,
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

class EntryType(Base):
    __tablename__ = 'entry_types'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)

    def __init__(self, title, description):
        self.title = title
        self.description = description

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)

    entry_type_id = Column(Integer, ForeignKey('entry_types.id'))
    entry_type = relationship("EntryType")

    baby_id = Column(Integer, ForeignKey('babies.id'))
    baby = relationship("Baby")

    start = Column(DateTime)
    end = Column(DateTime, nullable=True)
    duration = Column(Time, nullable=True)

    amount = Column(Integer, nullable=True)
    note = Column(String, nullable=True)

    def __init__(self, entry_type, baby, start, end=None, duration=None, amount=None, note=None):
        self.entry_type = entry_type
        self.baby = baby
        self.start = start
        self.end = end
        self.duration = duration
        self.amount = amount
        self.note = note

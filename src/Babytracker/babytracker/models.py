import hashlib
from datetime import timedelta

from sqlalchemy import Column, ForeignKey, desc
from sqlalchemy import  String, Enum, Integer, Date, DateTime, Interval
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Allow, DENY_ALL

from babytracker.interfaces import VIEW_PERMISSION, EDIT_PERMISSION

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Root(object):
    """Root factory
    """

    _instance = None

    # Singleton factory - this class has no state anyway, but want to be
    # able to record lineage to it via ``__parent__``
    def __new__(cls, request=None):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # Traversal

    __name__ = None
    __parent__ = None

    def __getitem__(self, name):
        if '@' not in name:
            raise KeyError(name)

        session = DBSession()
        try:
            return session.query(User).filter_by(email=name).one()
        except NoResultFound:
            raise KeyError(name)

    # Security

    __acl__ = [
            DENY_ALL,
        ]

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    password = Column(String)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = self._hash_password(password)

    # Operations

    @classmethod
    def _hash_password(self, password):
        return hashlib.sha1(password).hexdigest()

    @classmethod
    def authenticate(cls, email, password):
        """Attempt to find and return a ``User`` object with the given username
        and password. The password should be in plain text as entered by
        the user. Returns ``None`` if no user could be found.
        """
        session = DBSession()
        try:
            return session.query(User).filter_by(
                email=email,
                password=cls._hash_password(password)
            ).one()
        except NoResultFound:
            return None

    def change_password(self, new_password):
        """Set a new password. ``new_password`` should be in plain text. The
        password will be stored hashed.
        """
        self.password = self._hash_password(new_password)

    # Traversal

    @property
    def __name__(self):
        return self.email

    @property
    def __parent__(self):
        return Root()

    def __getitem__(self, name):
        for baby in self.babies:
            if baby.__name__ == name:
                return baby
        raise KeyError(name)

    # Security

    @property
    def __acl__(self):
        return [
            (Allow, self.__name__, (VIEW_PERMISSION, EDIT_PERMISSION,)),
            DENY_ALL,
        ]

class Baby(Base):
    __tablename__ = 'babies'

    id = Column(Integer, primary_key=True)
    dob = Column(Date)
    name = Column(String)
    gender = Column(Enum('m', 'f'))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('babies', order_by=id))

    def __init__(self, user, dob, name, gender):
        self.user = user
        self.dob = dob
        self.name = name
        self.gender = gender
        self.entries = []

    # Operations

    def get_entries_between(self, start, end, entry_type=None):
        """Return a list of entries in reverse order between the start and end
        datetimes, inclusive
        """
        session = DBSession()

        cls = Entry
        if entry_type is not None:
            cls = entry_type

        query = session.query(cls).filter(cls.baby==self)

        if start is not None:
            query = query.filter(cls.start>=start)
        if end is not None:
            query = query.filter(cls.start<=end)

        return query.order_by(desc(cls.start))

    # Traversal

    @property
    def __name__(self):
        return self.name.strip().lower().replace(' ', '-')

    @property
    def __parent__(self):
        return self.user

    def __getitem__(self, name):
        entry_id = None
        try:
            entry_id = int(name)
        except:
            raise KeyError(name)

        session = DBSession()
        try:
            return session.query(Entry).filter_by(id=entry_id).one()
        except NoResultFound:
            raise KeyError(name)

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    start = Column(DateTime)
    end = Column(DateTime, nullable=True)
    note = Column(String, nullable=True)

    baby_id = Column(Integer, ForeignKey('babies.id'))
    baby = relationship("Baby", backref=backref('entries', order_by=start.desc))

    __mapper_args__ = {'polymorphic_on': type}

    def __init__(self, baby, start, end=None, note=None):
        self.baby = baby
        self.start = start
        self.end = end
        self.note = note

    # Traversal

    @property
    def __name__(self):
        return unicode(self.id)

    @property
    def __parent__(self):
        return self.baby

    def __getitem__(self, name):
        raise KeyError(name)

class BreastFeed(Entry):
    __mapper_args__ = {'polymorphic_identity': 'breast_feed'}

    left_duration = Column(Interval)
    right_duration = Column(Interval)

    def __init__(self, baby, start, left_duration=timedelta(0), right_duration=timedelta(0), end=None, note=None):
        super(BreastFeed, self).__init__(baby, start, end, note)
        self.left_duration = left_duration
        self.right_duration = right_duration

class BottleFeed(Entry):
    __mapper_args__ = {'polymorphic_identity': 'bottle_feed'}

    amount = Column(Integer)

    def __init__(self, baby, start, amount, end=None, note=None):
        super(BottleFeed, self).__init__(baby, start, end, note)
        self.amount = amount

class MixedFeed(BreastFeed):
    __mapper_args__ = {'polymorphic_identity': 'mixed_feed'}

    topup = Column(Integer)

    def __init__(self, baby, start, left_duration=timedelta(0), right_duration=timedelta(0), topup=0, end=None, note=None):
        self.baby = baby
        self.start = start
        self.left_duration = left_duration
        self.right_duration = right_duration
        self.topup = topup
        self.end = end
        self.note = note

class Sleep(Entry):
    __mapper_args__ = {'polymorphic_identity': 'sleep'}

    duration = Column(Interval)

    def __init__(self, baby, start, duration, end=None, note=None):
        super(Sleep, self).__init__(baby, start, end, note)
        self.duration = duration

class NappyChange(Entry):
    __mapper_args__ = {'polymorphic_identity': 'nappy_change'}

    contents = Column(Enum('wet', 'dirty', 'none'))

    def __init__(self, baby, start, contents, end=None, note=None):
        super(NappyChange, self).__init__(baby, start, end, note)
        self.contents = contents

# TODO: Other types of entries:
# - solid foods
# - play
# - development milestone

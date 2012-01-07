import unittest
from pyramid import testing

class TestModel(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from babytracker.models import DBSession, Base
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        from babytracker.models import DBSession
        DBSession.remove()
        testing.tearDown()

    def test_hierarchy(self):
        import transaction
        import hashlib
        import datetime
        from babytracker.models import DBSession, User, Baby, EntryType, Entry

        with transaction.manager:

            feed = EntryType(u"Feed", "A feeding")
            nappy = EntryType(u"Nappy", "Nappy change")

            DBSession.add(feed)
            DBSession.add(nappy)

            user = User('test@example.org', u'John Smith', hashlib.sha1('secret').hexdigest())
            baby1 = Baby(datetime.date(2001,11,25), u"Jill Smith", 'f', user)
            baby2 = Baby(datetime.date(2011,11,25), u"Bill Smith", 'm', user)
            DBSession.add(user)

            self.assertEqual(user.babies, [baby1, baby2])

            entry = Entry(feed, baby1, datetime.datetime.now(), amount=100, note=u"Bottle")
            DBSession.add(entry)

            self.assertEqual(entry.baby, baby1)
            self.assertEqual(entry.entry_type, feed)

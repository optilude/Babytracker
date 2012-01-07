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
        from babytracker.models import DBSession, User, Baby
        from babytracker.models import BreastFeed, BottleFeed, MixedFeed, Sleep, Nappy

        with transaction.manager:

            user = User('test@example.org', u'John Smith', hashlib.sha1('secret').hexdigest())
            baby1 = Baby(datetime.date(2001,11,25), u"Jill Smith", 'f', user)
            baby2 = Baby(datetime.date(2011,11,25), u"Bill Smith", 'm', user)
            DBSession.add(user)

            self.assertEqual(user.babies, [baby1, baby2])

            breastFeed = BreastFeed(baby1, datetime.datetime.now(), datetime.timedelta(10))
            bottleFeed = BottleFeed(baby1, datetime.datetime.now(), 100)
            mixedFeed = MixedFeed(baby1, datetime.datetime.now(), datetime.timedelta(10), 100)
            sleep = Sleep(baby1, datetime.datetime.now(), datetime.timedelta(30))
            nappy = Nappy(baby1, datetime.datetime.now(), 'wet')

            DBSession.add(breastFeed)
            DBSession.add(bottleFeed)
            DBSession.add(mixedFeed)
            DBSession.add(sleep)
            DBSession.add(nappy)

            self.assertEqual(breastFeed.baby, baby1)
            self.assertEqual(bottleFeed.baby, baby1)
            self.assertEqual(mixedFeed.baby, baby1)
            self.assertEqual(sleep.baby, baby1)
            self.assertEqual(nappy.baby, baby1)


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

    def test_user(self):
        import transaction
        import hashlib
        from babytracker.models import Root, DBSession, User
        from pyramid.security import Allow, DENY_ALL

        with transaction.manager:

            session = DBSession()

            session.add(User(u'test@example.org', u'John Smith', 'secret'))
            user = session.query(User).filter_by(email=u'test@example.org').one()

            self.assertEqual(user.email, u'test@example.org')
            self.assertEqual(user.name, u'John Smith')
            self.assertEqual(user.password, hashlib.sha1('secret').hexdigest())
            self.assertEqual(user.__name__, u'test@example.org')
            self.assertEqual(user.__parent__, Root())

            self.assertEqual(user.__acl__, [
                (Allow, u'test@example.org', ('view', 'edit',)),
                DENY_ALL,
            ])

    def test_user_authenticate_success(self):
        import transaction
        from babytracker.models import DBSession, User

        with transaction.manager:
            session = DBSession()

            session.add(User(u'test1@example.org', u'John Smith', 'secret'))
            session.add(User(u'test2@example.org', u'Jill Smith', 'foobar'))

            user = User.authenticate(u'test1@example.org', 'secret')
            self.assertEqual(user.__name__, u'test1@example.org')

    def test_user_authenticate_unknown_user(self):
        import transaction
        from babytracker.models import DBSession, User

        with transaction.manager:
            session = DBSession()

            session.add(User(u'test1@example.org', u'John Smith', 'secret'))
            session.add(User(u'test2@example.org', u'Jill Smith', 'foobar'))

            user = User.authenticate(u'test3@example.org', 'secret')
            self.assertEqual(user, None)

    def test_user_authenticate_incorrect_password(self):
        import transaction
        from babytracker.models import DBSession, User

        with transaction.manager:
            session = DBSession()

            session.add(User(u'test1@example.org', u'John Smith', 'secret'))
            session.add(User(u'test2@example.org', u'Jill Smith', 'foobar'))

            user = User.authenticate(u'test3@example.org', 'sikrit')
            self.assertEqual(user, None)

    def test_user_change_password(self):
        import hashlib
        from babytracker.models import User

        user = User(u'test1@example.org', u'John Smith', 'secret')
        self.assertEqual(user.password, hashlib.sha1('secret').hexdigest())

        user.change_password('sikrit')
        self.assertEqual(user.password, hashlib.sha1('sikrit').hexdigest())

    def test_baby(self):
        import transaction
        import datetime
        from babytracker.models import DBSession, User, Baby

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            session.add(Baby(user, datetime.date(2001,11,25), u"Jill Smith", 'f'))
            session.add(Baby(user, datetime.date(2011,11,25), u"Bill Smith", 'm'))

            baby1 = session.query(Baby).filter_by(name=u"Jill Smith").one()
            baby2 = session.query(Baby).filter_by(name=u"Bill Smith").one()

            self.assertEqual(user.babies, [baby1, baby2])

            self.assertEqual(baby1.user, user)
            self.assertEqual(baby1.dob, datetime.date(2001, 11, 25))
            self.assertEqual(baby1.name, u"Jill Smith")
            self.assertEqual(baby1.gender, 'f')
            self.assertEqual(baby1.__name__, u"jill-smith")
            self.assertEqual(baby1.__parent__, user)

    def test_root_singleton(self):
        from babytracker.models import Root

        self.assertTrue(Root() is Root())

    def test_root_traversal(self):
        import transaction
        from babytracker.models import Root, DBSession, User

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            root = Root()

            self.assertEqual(root['test@example.org'], user)
            self.assertRaises(KeyError, root.__getitem__, 'foo@bar.com')
            self.assertRaises(KeyError, root.__getitem__, 'frobble')

    def test_user_traversal(self):
        import transaction
        import datetime
        from babytracker.models import DBSession, User, Baby

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            session.add(Baby(user, datetime.date(2001,11,25), u"Jill Smith", 'f'))
            session.add(Baby(user, datetime.date(2011,11,25), u"Bill Smith", 'm'))

            baby1 = session.query(Baby).filter_by(name=u"Jill Smith").one()
            baby2 = session.query(Baby).filter_by(name=u"Bill Smith").one()

            self.assertEqual(user['jill-smith'], baby1)
            self.assertEqual(user['bill-smith'], baby2)
            self.assertRaises(KeyError, user.__getitem__, 'Jill Smith')
            self.assertRaises(KeyError, user.__getitem__, 'Jack Smith')

    def test_entries(self):
        import transaction
        import datetime
        from babytracker.models import DBSession, User, Baby
        from babytracker.models import BreastFeed, BottleFeed, MixedFeed, Sleep, NappyChange

        baby_id = None

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            baby = Baby(user, datetime.date(2001,11,25), u"Jill Smith", 'f')
            session.add(baby)

            session.add(BreastFeed(baby,
                start=datetime.datetime(2012, 1, 1, 12, 0, 0),
                left_duration=datetime.timedelta(minutes=10),
                right_duration=datetime.timedelta(minutes=25),
                end=datetime.datetime(2012, 1, 1, 12, 30, 0),
                note=u"Fussy",
            ))

            session.add(BottleFeed(baby,
                start=datetime.datetime(2012, 1, 1, 14, 0, 0),
                amount=130,
                end=datetime.datetime(2012, 1, 1, 14, 30, 0),
                note=u"Calm",
            ))

            session.add(MixedFeed(baby,
                start=datetime.datetime(2012, 1, 1, 13, 0, 0),
                left_duration=datetime.timedelta(minutes=7),
                right_duration=datetime.timedelta(minutes=12),
                topup=110,
                end=datetime.datetime(2012, 1, 1, 13, 30, 0),
                note=u"Happy",
            ))

            session.add(Sleep(baby,
                start=datetime.datetime(2012, 1, 1, 15, 0, 0),
                duration=datetime.timedelta(minutes=45),
                end=datetime.datetime(2012, 1, 1, 15, 45, 0),
                note=u"Crying",
            ))

            session.add(NappyChange(baby,
                start=datetime.datetime(2012, 1, 1, 16, 0, 0),
                contents='wet',
                end=datetime.datetime(2012, 1, 1, 16, 5, 0),
                note=u"Angry",
            ))

            session.flush()
            baby_id = baby.id

        # Re-fetch in a different transaction to test ordering of entries
        session = DBSession()
        baby = session.query(Baby).get(baby_id)
        self.assertEqual(len(baby.entries), 5)

        # Expected order
        nappy, sleep, bottle, mixed, breast = baby.entries

        self.assertTrue(isinstance(nappy, NappyChange))
        self.assertEqual(nappy.baby.id, baby_id)
        self.assertEqual(nappy.start, datetime.datetime(2012, 1, 1, 16, 0, 0))
        self.assertEqual(nappy.contents, 'wet')
        self.assertEqual(nappy.end, datetime.datetime(2012, 1, 1, 16, 5, 0))
        self.assertEqual(nappy.note, u"Angry")

        self.assertTrue(isinstance(sleep, Sleep))
        self.assertEqual(sleep.start, datetime.datetime(2012, 1, 1, 15, 0, 0))
        self.assertEqual(sleep.duration, datetime.timedelta(minutes=45))
        self.assertEqual(sleep.end, datetime.datetime(2012, 1, 1, 15, 45, 0))
        self.assertEqual(sleep.note, u"Crying")

        self.assertTrue(isinstance(bottle, BottleFeed))
        self.assertEqual(bottle.start, datetime.datetime(2012, 1, 1, 14, 0, 0))
        self.assertEqual(bottle.amount, 130)
        self.assertEqual(bottle.end, datetime.datetime(2012, 1, 1, 14, 30, 0))
        self.assertEqual(bottle.note, u"Calm")

        self.assertTrue(isinstance(mixed, MixedFeed))
        self.assertEqual(mixed.start, datetime.datetime(2012, 1, 1, 13, 0, 0))
        self.assertEqual(mixed.left_duration, datetime.timedelta(minutes=7))
        self.assertEqual(mixed.right_duration, datetime.timedelta(minutes=12))
        self.assertEqual(mixed.topup, 110)
        self.assertEqual(mixed.end, datetime.datetime(2012, 1, 1, 13, 30, 0))
        self.assertEqual(mixed.note, u"Happy")

        self.assertTrue(isinstance(breast, BreastFeed))
        self.assertEqual(breast.start, datetime.datetime(2012, 1, 1, 12, 0, 0))
        self.assertEqual(breast.left_duration, datetime.timedelta(minutes=10))
        self.assertEqual(breast.right_duration, datetime.timedelta(minutes=25))
        self.assertEqual(breast.end, datetime.datetime(2012, 1, 1, 12, 30, 0))
        self.assertEqual(breast.note, u"Fussy")

    def test_baby_traversal(self):
        import transaction
        import datetime
        from babytracker.models import DBSession, User, Baby
        from babytracker.models import BreastFeed, BottleFeed

        baby_id = breast_id = bottle_id = None

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            baby = Baby(user, datetime.date(2001,11,25), u"Jill Smith", 'f')
            session.add(baby)

            breast = BreastFeed(baby,
                start=datetime.datetime(2012, 1, 1, 12, 0, 0),
                left_duration=datetime.timedelta(minutes=10),
                right_duration=datetime.timedelta(minutes=25)
            )

            bottle = BottleFeed(baby,
                start=datetime.datetime(2012, 1, 1, 14, 0, 0),
                amount=130
            )

            session.add(breast)
            session.add(bottle)
            session.flush()

            baby_id = baby.id
            breast_id = breast.id
            bottle_id = bottle.id

        session = DBSession()
        baby = session.query(Baby).get(baby_id)

        breast = baby[str(breast_id)]
        self.assertTrue(isinstance(breast, BreastFeed))
        self.assertEqual(breast.id, breast_id)

        bottle = baby[bottle_id]
        self.assertTrue(isinstance(bottle, BottleFeed))
        self.assertEqual(bottle.id, bottle_id)

        self.assertRaises(KeyError, baby.__getitem__, 'notastring')
        self.assertRaises(KeyError, baby.__getitem__, '9999')

    def test_baby_get_entries_between(self):
        import transaction
        import datetime
        from babytracker.models import DBSession, User, Baby
        from babytracker.models import BreastFeed, BottleFeed, MixedFeed, Sleep, NappyChange

        baby_id = None

        with transaction.manager:

            session = DBSession()

            user = User(u'test@example.org', u'John Smith', 'secret')
            session.add(user)

            baby = Baby(user, datetime.date(2001,11,25), u"Jill Smith", 'f')
            session.add(baby)

            session.add(BreastFeed(baby,
                start=datetime.datetime(2012, 1, 1, 12, 0, 0),
                left_duration=datetime.timedelta(minutes=10),
                right_duration=datetime.timedelta(minutes=25),
                end=datetime.datetime(2012, 1, 1, 12, 30, 0),
                note=u"breast1",
            ))

            session.add(BottleFeed(baby,
                start=datetime.datetime(2012, 1, 1, 14, 0, 0),
                amount=130,
                end=datetime.datetime(2012, 1, 1, 14, 30, 0),
                note=u"bottle1",
            ))

            session.add(MixedFeed(baby,
                start=datetime.datetime(2012, 1, 1, 13, 0, 0),
                left_duration=datetime.timedelta(minutes=7),
                right_duration=datetime.timedelta(minutes=12),
                topup=110,
                end=datetime.datetime(2012, 1, 1, 13, 30, 0),
                note=u"mixed1",
            ))

            session.add(Sleep(baby,
                start=datetime.datetime(2012, 1, 2, 15, 0, 0),
                duration=datetime.timedelta(minutes=45),
                end=datetime.datetime(2012, 1, 2, 15, 45, 0),
                note=u"sleep1",
            ))

            session.add(NappyChange(baby,
                start=datetime.datetime(2012, 1, 2, 16, 0, 0),
                contents='wet',
                end=datetime.datetime(2012, 1, 2, 16, 5, 0),
                note=u"nappy1",
            ))

            session.add(NappyChange(baby,
                start=datetime.datetime(2012, 1, 2, 17, 0, 0),
                contents='wet',
                end=datetime.datetime(2012, 1, 2, 17, 5, 0),
                note=u"nappy2",
            ))

            session.flush()
            baby_id = baby.id

        session = DBSession()
        baby = session.query(Baby).get(baby_id)

        # Total order:
        # nappy2, nappy1, sleep1, bottle1, mixed1, breast1

        entries = baby.get_entries_between(start=None, end=None)
        self.assertEqual(
            [u'nappy2', u'nappy1', u'sleep1', u'bottle1', u'mixed1', u'breast1'],
            [e.note for e in entries]
        )

        entries = baby.get_entries_between(start=None, end=None, entry_type=NappyChange)
        self.assertEqual(
            [u'nappy2', u'nappy1'],
            [e.note for e in entries]
        )

        entries = baby.get_entries_between(start=datetime.datetime(2012, 1, 1, 14, 0, 0), end=None)
        self.assertEqual(
            [u'nappy2', u'nappy1', u'sleep1', u'bottle1'],
            [e.note for e in entries]
        )

        entries = baby.get_entries_between(start=None, end=datetime.datetime(2012, 1, 2, 15, 0, 0))
        self.assertEqual(
            [u'sleep1', u'bottle1', u'mixed1', u'breast1'],
            [e.note for e in entries]
        )

        entries = baby.get_entries_between(start=datetime.datetime(2012, 1, 1, 14, 0, 0), end=datetime.datetime(2012, 1, 2, 15, 0, 0))
        self.assertEqual(
            [u'sleep1', u'bottle1'],
            [e.note for e in entries]
        )

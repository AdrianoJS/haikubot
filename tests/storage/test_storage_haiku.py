from datetime import timedelta, datetime

from sqlalchemy import create_engine

from haikubot.storage.persistence import Persistence

import unittest

EX_HAIKU = "This is an\nVery Cool\nHaiku"


class StorageHaikuTest(unittest.TestCase):
    store = None

    @classmethod
    def setUpClass(cls):
        cls.store = Persistence(db=create_engine('sqlite:///:memory:'))

    @classmethod
    def tearDownClass(cls):
        cls.store.connection.close()

    def tearDown(self):
        self.store._purge()

    def test_put_haiku_unposted(self):
        self.store.put_haiku(EX_HAIKU + '1', 'Karl the Tester', posted=False)
        haiku = self.store.get_haiku(1)
        self.assertEqual(haiku['haiku'], EX_HAIKU + '1')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], False)

    def test_put_haiku_posted_false_default(self):
        self.store.put_haiku(EX_HAIKU + '2', 'Karl the Tester')
        haiku = self.store.get_haiku(1)
        self.assertEqual(haiku['haiku'], EX_HAIKU + '2')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], False)

    def test_get_newest_haiku(self):
        self.store.put_haiku('This is not a\nBad Boo!\nFakeu', 'Earl the Fester')
        self.store.put_haiku(EX_HAIKU + '3', 'Karl the Tester')
        haiku = self.store.get_newest()
        self.assertEqual(haiku[0]['haiku'], EX_HAIKU + '3')
        self.assertEqual(haiku[0]['author'], 'Karl the Tester')
        self.assertEqual(haiku[0]['posted'], False)

    def test_set_posted(self):
        self.store.put_haiku(EX_HAIKU + '4', 'Karl the Tester', posted=False)
        self.store.set_posted(1)
        haiku = self.store.get_haiku(1)
        self.assertEqual(haiku['haiku'], EX_HAIKU + '4')
        self.assertEqual(haiku['author'], 'Karl the Tester')
        self.assertEqual(haiku['posted'], True)

    def test_get_unposted(self):
        self.store.put_haiku(EX_HAIKU + '5', 'Karl One', posted=False)
        self.store.put_haiku(EX_HAIKU + '6', 'Carl Two', posted=True)
        self.store.put_haiku(EX_HAIKU + '7', 'Curl Three', posted=False)
        posted = self.store.get_unposted()
        self.assertEqual(posted[0]['author'], 'Karl One')
        self.assertEqual(posted[1]['author'], 'Curl Three')

    def test_get_haiku_by_author_default_amount(self):
        self.store.put_haiku(EX_HAIKU + '8', 'Karl One', posted=False)
        self.store.put_haiku(EX_HAIKU + '9', 'Carl Two', posted=True)
        self.store.put_haiku(EX_HAIKU + '10', 'Karl Three', posted=False)
        self.store.put_haiku(EX_HAIKU + '11', 'Karl Four', posted=False)
        posted = self.store.get_by('Karl')
        self.assertEqual(posted[0]['author'], 'Karl Four')
        self.assertTrue(len(posted) == 3)

    def test_get_haiku_by_author_set_amount(self):
        self.store.put_haiku(EX_HAIKU + '12', 'Karl One', posted=False)
        self.store.put_haiku(EX_HAIKU + '13', 'Carl Two', posted=True)
        self.store.put_haiku(EX_HAIKU + '14', 'Karl Three', posted=False)
        self.store.put_haiku(EX_HAIKU + '15', 'Karl Four', posted=False)
        posted = self.store.get_by('Karl', num=2)
        self.assertEqual(posted[0]['author'], 'Karl Four')
        self.assertEqual(posted[1]['author'], 'Karl Three')
        self.assertTrue(len(posted) == 2)

    def test_get_stats(self):
        correct = [('Karl Four', 3), ('Karl One', 2), ('Carl Two', 1), ('Karl Three', 1)]
        self.store.put_haiku(EX_HAIKU + '12', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '13', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '14', 'Carl Two')
        self.store.put_haiku(EX_HAIKU + '15', 'Karl Three')
        self.store.put_haiku(EX_HAIKU + '16', 'Karl Four')
        self.store.put_haiku(EX_HAIKU + '17', 'Karl Four')
        self.store.put_haiku(EX_HAIKU + '18', 'Karl Four')
        posted = self.store.get_haiku_stats()
        self.assertEqual(correct, posted)

    def test_get_stats_limit_top(self):
        correct = [('Karl Four', 3), ('Karl One', 2)]
        self.store.put_haiku(EX_HAIKU + '12', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '13', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '14', 'Carl Two')
        self.store.put_haiku(EX_HAIKU + '15', 'Karl Three')
        self.store.put_haiku(EX_HAIKU + '16', 'Karl Four')
        self.store.put_haiku(EX_HAIKU + '17', 'Karl Four')
        self.store.put_haiku(EX_HAIKU + '18', 'Karl Four')
        posted = self.store.get_haiku_stats(top_num=2)
        self.assertEqual(correct, posted)

    def test_get_all_haiku(self):
        self.store.put_haiku(EX_HAIKU + '1', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '2', 'Karl One')
        self.store.put_haiku(EX_HAIKU + '3', 'Carl Two')
        self.store.put_haiku(EX_HAIKU + '4', 'Karl Three')
        haiku = self.store.get_all_haiku()
        self.assertEqual(4, len(haiku))

    def test_get_all_haiku_within_3(self):
        self.store.put_haiku(EX_HAIKU + '1', 'Karl One', date=datetime.now() - timedelta(weeks=2))
        self.store.put_haiku(EX_HAIKU + '2', 'Karl One', date=datetime.now() - timedelta(weeks=3) + timedelta(days=1))
        self.store.put_haiku(EX_HAIKU + '3', 'Carl Two', date=datetime.now() - timedelta(weeks=4))
        self.store.put_haiku(EX_HAIKU + '4', 'Karl Three', date=datetime.now() - timedelta(weeks=5))
        haiku = self.store.get_all_haiku_weeks(3)
        self.assertEqual(2, len(haiku))

    def test_get_all_haiku_within_6(self):
        self.store.put_haiku(EX_HAIKU + '1', 'Karl One', date=datetime.now() - timedelta(weeks=2))
        self.store.put_haiku(EX_HAIKU + '2', 'Karl One', date=datetime.now() - timedelta(weeks=3) + timedelta(days=1))
        self.store.put_haiku(EX_HAIKU + '3', 'Carl Two', date=datetime.now() - timedelta(weeks=4))
        self.store.put_haiku(EX_HAIKU + '4', 'Karl Three', date=datetime.now() - timedelta(weeks=5))
        haiku = self.store.get_all_haiku_weeks(6)
        self.assertEqual(4, len(haiku))

from django.contrib.auth.models import User

__author__ = 'sparky'
import datetime

from django.utils import timezone
from django.test import TestCase
# For those of you who are curious
from model_mommy import mommy
from django.core.urlresolvers import reverse
from django.test.client import Client
from approval_polls.models import Poll


class TestPoll(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_closed(self):
        '''Can we tell if a poll is closed?
           A poll should be closed if the current date is
           passed the closed_date member on the model'''

        close_date = timezone.datetime(2012, 1, 1, tzinfo=timezone.UTC()) #first we need a date in the past
        open_date = timezone.datetime(2011, 12, 12, tzinfo=timezone.UTC()) # and an open date earlier than that.
        poll = mommy.make(Poll, close_date=close_date, open_date=open_date)
        result = poll.is_closed()
        self.assertTrue(result)

    def test_is_closed_false(self):
        '''Can we tell if a poll is still open?
        A poll should still be open if it's closed date is still
        in the future'''

        #first we need a date in the future
        close_date = timezone.now() + timezone.timedelta(days=20)
        # and an open date earlier than that.
        open_date = timezone.datetime(2011, 12, 12, tzinfo=timezone.UTC())

        poll = mommy.make(Poll, close_date=close_date, open_date=open_date)
        result = poll.is_closed()
        self.assertFalse(result)


class TestEditPoll(TestCase):

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('test', 'test@example.com', 'test')
        self.client.login(username='test', password='test')
        open_date = timezone.now()
        close_date = timezone.now() + timezone.timedelta(days=30)
        self.poll = mommy.make(Poll, user=user, open_date=open_date,
                               close_date=close_date, pub_date=open_date)

    def tearDown(self):
        pass

    def test_edit_poll(self):
        '''Can we edit the poll's close date?'''
        pass

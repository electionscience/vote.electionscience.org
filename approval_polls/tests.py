import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User

from approval_polls.models import Poll, Choice

def create_poll(question, days=0, ballots=0):
    """
    Creates a poll with the given `question` published the given number of
    `days` offset to now (negative for polls published in the past,
    positive for polls that have yet to be published).
    """
    return Poll.objects.create(question=question,
        pub_date=timezone.now() + datetime.timedelta(days=days), ballots=ballots)

class PollIndexTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('approval_polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed on the
        index page.
        """
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_poll(question="Past poll.", days=-30)
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_poll(question="Past poll 1.", days=-30)
        create_poll(question="Past poll 2.", days=-5)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
             ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )

    def test_index_view_with_empty_page(self):
        """
        If an empty page of polls is requested, then the last page of polls is returned.
        """
        create_poll(question="Empty page poll.")
        response = self.client.get('/approval_polls/?page=2')
        self.assertContains(response, '(page 1 of 1)', status_code=200)

class PollDetailTests(TestCase):
    def test_detail_view_with_a_future_poll(self):
        """
        The detail view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        future_poll = create_poll(question='Future poll.', days=5)
        response = self.client.get(reverse('approval_polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a poll with a pub_date in the past should display
        the poll's question.
        """
        past_poll = create_poll(question='Past Poll.', days=-5)
        response = self.client.get(reverse('approval_polls:detail', args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_detail_view_with_a_choice(self):
        """
        The detail view of a poll with a choice should display the
        choice's text.
        """
        poll = create_poll(question='Choice poll.')
        poll.choice_set.create(choice_text='Choice text.', votes=0)
        response = self.client.get(reverse('approval_polls:detail', args=(poll.id,)))
        self.assertContains(response, 'Choice text.', status_code=200)

class PollResultsTests(TestCase):
    def test_results_view_with_no_ballots(self):
        """
        Results page of a poll with a choice shows 0 votes (0%), 0 votes on 0 ballots.
        """
        poll = create_poll(question='Choice poll.')
        poll.choice_set.create(choice_text='Choice text.', votes=0)
        response = self.client.get(reverse('approval_polls:results', args=(poll.id,)))
        self.assertContains(response, '0&nbsp;votes (0%)', status_code=200)
        self.assertContains(response, '0 votes on 0 ballots', status_code=200)

    def test_results_view_with_ballots(self):
        """
        Results page of a poll with a choice and ballots shows the correct percentage,
        total vote count, and total ballot count.
        """
        poll = create_poll(question='Choice poll.', ballots=2)
        poll.choice_set.create(choice_text='Choice text.', votes=1)
        response = self.client.get(reverse('approval_polls:results', args=(poll.id,)))
        self.assertContains(response, '1&nbsp;vote (50%)', status_code=200)
        self.assertContains(response, '1 vote on 2 ballots', status_code=200)

class PollVoteTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_vote_view_counts_increase(self):
        """
        Voting in a poll increases the count for selected choices, but not for unselected
        ones, and also increases the ballot count.
        """
        poll = create_poll(question='Vote poll.', ballots=100)
        poll.choice_set.create(choice_text='Choice 1.', votes=10)
        poll.choice_set.create(choice_text='Choice 2.', votes=20)
        response  = self.client.post('/approval_polls/'+str(poll.id)+'/vote/', data={'choice2':''}, follow=True)
        self.assertContains(response, '10&nbsp;votes')
        self.assertContains(response, '21&nbsp;votes')
        self.assertContains(response, '101 ballots', status_code=200)

class PollCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
	user = User.objects.create_user('test','test@example.com','test')
	user.save()
	self.client.login(username='test', password='test')

    def test_create_page_exists(self):
	"""
	The create a poll form exists
	"""
	response = self.client.post('/approval_polls/create/')
	self.assertEquals(response.status_code, 200)

    def test_create_redirects_to_detail(self):
        """
        Creating a new poll leads to the new polls vote page.
        """
        poll_data = {
            'question':'Create poll.',
            'choice1' :'Choice 1.',
            'choice2' :'Choice 2.',
            }        
        response = self.client.post('/approval_polls/created/', poll_data, follow=True)
        self.assertContains(response, 'Create poll.', status_code=200)
        self.assertContains(response, 'Choice 1.')
        self.assertContains(response, 'Choice 2.')
        self.assertContains(response, 'See Results')

    def test_create_with_no_question(self):
        """
        No question should return an error message.
        """
        response = self.client.post('/approval_polls/created/', {'choice1':'Choice 1.'}, follow=True)
        self.assertContains(response, 'You have to ask a question!', status_code=200)

    def test_crete_with_blank_question(self):
        """
        Blank question should return an error message.
        """
        response = self.client.post('/approval_polls/created/', {'question':'', 'choice1':'Choice 1.'}, follow=True)
        self.assertContains(response, 'You have to ask a question!', status_code=200)

    def test_create_skips_blank_choices(self):
        """
        A blank choice doesn't appear in the poll (but later ones do)
        """
        poll_data = {
            'question':'Create poll.',
            'choice1' :'',
            'choice2' :'Choice 2.',
            }        
        response = self.client.post('/approval_polls/created/', poll_data, follow=True)
        self.assertContains(response, 'Create poll.', status_code=200)
        self.assertNotContains(response, 'Choice 1.')
        self.assertContains(response, 'Choice 2.')
        self.assertContains(response, 'See Results')


import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User

from approval_polls.models import Poll


def create_poll(question, username="user1", days=0, ballots=0, vtype=2):
    """
    Creates a poll with the given `question` published the given number of
    `days` offset to now (negative for polls published in the past,
    positive for polls that have yet to be published), and user as the
    foreign key pointing to the user model. Defaults to vote type 2 for
    this poll (1 - Does not require authentication to vote, 2 - Requires
    authentication to vote).
    """
    poll = Poll.objects.create(
        question=question,
        pub_date=timezone.now() + datetime.timedelta(days=days),
        user=User.objects.create_user(username, 'test@example.com', 'test'),
        vtype=vtype
    )

    for _ in range(ballots):
        create_ballot(poll)

    return poll


def create_ballot(poll, timestamp=timezone.now(), ip='127.0.0.1'):
    """
    Creates a ballot for the given `poll`, submitted at `timestamp` by `ip`.
    """
    return poll.ballot_set.create(timestamp=timestamp)


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
        Polls with a pub_date in the past should be displayed on the
        index page.
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_poll(question="Past poll.", days=-30, vtype=1)
        create_poll(question="Future poll.", username="user2", days=30,
                    vtype=1)
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
        create_poll(question="Past poll 2.", username="user2", days=-5)
        response = self.client.get(reverse('approval_polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )

    def test_index_view_with_empty_page(self):
        """
        If an empty page of polls is requested, then the last page of
        polls is returned.
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
        response = self.client.get(reverse('approval_polls:detail',
                                   args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a poll with a pub_date in the past should display
        the poll's question.
        """
        past_poll = create_poll(question='Past Poll.', days=-5)
        response = self.client.get(reverse('approval_polls:detail',
                                   args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_detail_view_with_a_choice(self):
        """
        The detail view of a poll with a choice should display the
        choice's text.
        """
        poll = create_poll(question='Choice poll.')
        poll.choice_set.create(choice_text='Choice text.')
        response = self.client.get(reverse('approval_polls:detail',
                                   args=(poll.id,)))
        self.assertContains(response, 'Choice text.', status_code=200)


class PollResultsTests(TestCase):
    def test_results_view_with_no_ballots(self):
        """
        Results page of a poll with a choice shows 0 votes (0%),
        0 votes on 0 ballots.
        """
        poll = create_poll(question='Choice poll.')
        poll.choice_set.create(choice_text='Choice text.')
        response = self.client.get(reverse('approval_polls:results',
                                   args=(poll.id,)))
        self.assertContains(response, '0 votes (0%)', status_code=200)
        self.assertContains(response, '0 votes on 0 ballots', status_code=200)

    def test_results_view_with_ballots(self):
        """
        Results page of a poll with a choice and ballots shows the correct
        percentage, total vote count, and total ballot count.
        """
        poll = create_poll(question='Choice poll.', ballots=1)
        choice = poll.choice_set.create(choice_text='Choice text.')
        create_ballot(poll).vote_set.create(choice=choice)
        response = self.client.get(reverse('approval_polls:results',
                                   args=(poll.id,)))
        self.assertContains(response, '1 vote (50%)', status_code=200)
        self.assertContains(response, '1 vote on 2 ballots', status_code=200)


class PollVoteTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_vote_view_counts_increase(self):
        """
        Voting in a poll increases the count for selected choices,
        but not for unselected ones, and also increases the ballot count.
        """
        poll = create_poll(question='Vote poll.', ballots=80, vtype=1)
        choice1 = poll.choice_set.create(choice_text='Choice 1.')
        choice2 = poll.choice_set.create(choice_text='Choice 2.')
        for _ in range(10):
            create_ballot(poll).vote_set.create(choice=choice1)
        for _ in range(10):
            create_ballot(poll).vote_set.create(choice=choice2)
        response = self.client.post('/approval_polls/'+str(poll.id)+'/vote/',
                                    data={'choice2': ''},
                                    follow=True)
        self.assertContains(response, '10 votes')
        self.assertContains(response, '21 votes')
        self.assertContains(response, '101 ballots', status_code=200)


class MyPollTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_poll(question="question1", days=-5, vtype=1)
        create_poll(question="question2", username="user2", days=-5, vtype=1)

    def test_redirect_when_not_logged_in(self):
        """
        If the user is not logged in then redirect to the login page
        """
        response = self.client.get(reverse('approval_polls:my_polls'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=/approval_polls/my-polls/',
            status_code=302,
            target_status_code=200
        )

    def test_display_only_user_polls(self):
        """
        Only polls created by the logged in user should be displayed.
        """
        self.client.login(username='user1', password='test')
        response = self.client.get(reverse('approval_polls:my_polls'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: question1>']
        )


class PollCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user('test', 'test@example.com', 'test')
        self.client.login(username='test', password='test')

    def test_create_page_exists(self):
        """
        The create a poll form exists.
        """
        response = self.client.post('/approval_polls/create/')
        self.assertEquals(response.status_code, 200)

    def test_create_shows_iframe_code(self):
        """
        Creating a new poll shows a HTML snippet to embed the new poll
        with an iframe.
        """
        poll_data = {
            'question': 'Create poll.',
            'choice1': 'Choice 1.',
            'radio-poll-type': '1',
        }
        response = self.client.post(
            '/approval_polls/create/',
            poll_data,
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'approval_polls/embed_instructions.html'
        )
        self.assertTrue('/approval_polls/1' in response.context['link'])

    def test_create_with_no_question(self):
        """
        No question should return an error message.
        """
        response = self.client.post(
            '/approval_polls/create/',
            {'choice1': 'Choice 1.'},
            follow=True
        )
        self.assertContains(
            response,
            'The question is missing',
            status_code=200
        )

    def test_create_with_blank_question(self):
        """
        Blank question should return an error message.
        """
        response = self.client.post(
            '/approval_polls/create/',
            {'question': '', 'choice1': 'Choice 1.'},
            follow=True
        )
        self.assertContains(
            response,
            'The question is missing',
            status_code=200
        )

    def test_create_skips_blank_choices(self):
        """
        A blank choice doesn't appear in the poll (but later ones do)
        """
        poll_data = {
            'question': 'Create poll.',
            'choice1': '',
            'choice2': 'Choice 2.',
            'radio-poll-type': '1',
            }
        self.client.post('/approval_polls/create/', poll_data, follow=True)
        response = self.client.get('/approval_polls/1/', follow=True)
        self.assertContains(response, 'Create poll.', status_code=200)
        self.assertNotContains(response, 'Choice 1.')
        self.assertContains(response, 'Choice 2.')
        self.assertContains(response, 'See Results')

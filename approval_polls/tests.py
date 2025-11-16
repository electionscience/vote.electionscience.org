import datetime

import structlog
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from approval_polls.models import Ballot, Choice, Poll, Vote, VoteInvitation

logger = structlog.get_logger(__name__)


def queryset_to_list_string(queryset):
    """Converts a queryset to a list of its items' string representations."""
    return [str(item) for item in queryset]


def page_to_list_string(page):
    """Converts a Page object to a list of its items' string representations."""
    return queryset_to_list_string(page.object_list)


def create_poll(
    question,
    username="user1",
    email="user1@example.com",
    days=0,
    ballots=0,
    vtype=2,
    close_date=None,
    is_private=False,
    is_suspended=False,
):
    """
    Creates a poll with the given `question` published the given number of
    `days` offset to now (negative for polls published in the past,
    positive for polls that have yet to be published), and user as the
    foreign key pointing to the user model. Defaults to vote type 2 for
    this poll (1 - Does not require authentication to vote, 2 - Requires
    authentication to vote, 3 - Email Invitation to vote).
    """
    poll = Poll.objects.create(
        question=question,
        pub_date=timezone.now() + datetime.timedelta(days=days),
        user=User.objects.create_user(
            username, "".join([username, "@example.com"]), "test"
        ),
        vtype=vtype,
        close_date=close_date,
        is_private=is_private,
        is_suspended=is_suspended,
    )

    for _ in range(ballots):
        create_ballot(poll)

    return poll


def create_ballot(poll, timestamp=timezone.now()):
    """
    Creates a ballot for the given `poll`, submitted at `timestamp` by `ip`.
    """
    return poll.ballot_set.create(timestamp=timestamp)


def create_vote_invitation(poll, email):
    """
    Creates a vote invitation for the given `poll`, with specified `email`
    """
    return poll.voteinvitation_set.create(email=email, key="xxx")


class PollIndexTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_poll_list"], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the
        index page.
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse("index"))
        user_polls = Poll.objects.filter(user__username="user1").order_by("id")

        self.assertQuerySetEqual(
            response.context["latest_poll_list"], map(repr, user_polls), transform=repr
        )

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_poll(question="Past poll.", days=-30, vtype=1)
        create_poll(
            question="Future poll.",
            username="user2",
            email="user2@example.com",
            days=30,
            vtype=1,
        )
        response = self.client.get(reverse("index"))

        # Get the queryset of past polls (which should be displayed)
        past_polls_qs = Poll.objects.filter(pub_date__lte=timezone.now()).order_by("id")
        past_polls_list_string = queryset_to_list_string(past_polls_qs)

        # Assuming 'latest_poll_list' is a simple QuerySet (not a Page object)
        actual_polls_list_string = queryset_to_list_string(
            response.context["latest_poll_list"]
        )

        self.assertListEqual(actual_polls_list_string, past_polls_list_string)

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_poll(question="Past poll 1.", days=-30)
        create_poll(
            question="Past poll 2.",
            username="user2",
            email="user2@example.com",
            days=-5,
        )
        response = self.client.get(reverse("index"))

        # Get the queryset of past polls (which should be displayed)
        past_polls_qs = Poll.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-id"
        )
        past_polls_list_string = queryset_to_list_string(past_polls_qs)

        # Assuming 'latest_poll_list' is a simple QuerySet (not a Page object)
        actual_polls_list_string = queryset_to_list_string(
            response.context["latest_poll_list"]
        )

        self.assertListEqual(actual_polls_list_string, past_polls_list_string)

    def test_index_view_with_empty_page(self):
        """
        If an empty page of polls is requested, then the last page of
        polls is returned.
        """
        create_poll(question="Empty page poll.")
        response = self.client.get("/?page=2")
        print(response)

        self.assertContains(response, "Page 1 of 1", status_code=200)


class PollDetailTests(TestCase):
    def test_detail_view_with_a_future_poll(self):
        """
        The detail view of a poll with a pub_date in the future should
        return a 404 not found.
        """
        future_poll = create_poll(question="Future poll.", days=5)
        response = self.client.get(reverse("detail", args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a poll with a pub_date in the past should display
        the poll's question.
        """
        past_poll = create_poll(question="Past Poll.", days=-5)
        response = self.client.get(reverse("detail", args=(past_poll.id,)))
        self.assertContains(response, past_poll.question, status_code=200)

    def test_detail_view_with_a_choice(self):
        """
        The detail view of a poll with a choice should display the
        choice's text.
        """
        poll = create_poll(question="Choice poll.")
        poll.choice_set.create(choice_text="Choice text.")
        response = self.client.get(reverse("detail", args=(poll.id,)))
        self.assertContains(response, "Choice text.", status_code=200)


class PollResultsTests(TestCase):
    def test_results_view_with_no_ballots(self):
        """
        Results page of a poll with a choice shows 0 votes (0%),
        0 votes on 0 ballots.
        """
        poll = create_poll(question="Choice poll.")
        poll.choice_set.create(choice_text="Choice text.")
        response = self.client.get(reverse("results", args=(poll.id,)))
        self.assertContains(response, "0 votes", status_code=200)

    def test_results_view_with_ballots(self):
        """
        Results page of a poll with a choice and ballots shows the correct
        percentage, total vote count, and total ballot count.
        """
        poll = create_poll(question="Choice poll.", ballots=1)
        choice = poll.choice_set.create(choice_text="Choice text.")
        create_ballot(poll).vote_set.create(choice=choice)
        response = self.client.get(reverse("results", args=(poll.id,)))
        self.assertContains(response, "1 vote", status_code=200)


class PollVoteTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_vote_view_counts_increase(self):
        """
        Voting in a poll increases the count for selected choices,
        but not for unselected ones, and also increases the ballot count.
        """
        poll = create_poll(question="Vote poll.", ballots=80, vtype=1)
        choice1 = poll.choice_set.create(choice_text="Choice 1.")
        choice2 = poll.choice_set.create(choice_text="Choice 2.")
        for _ in range(10):
            create_ballot(poll).vote_set.create(choice=choice1)
        for _ in range(21):
            create_ballot(poll).vote_set.create(choice=choice2)
        response = self.client.post(
            "/" + str(poll.id) + "/vote/",
            data={"choice2": ""},
            follow=True,
        )
        self.assertContains(response, "10 votes")
        self.assertContains(response, "22 votes")
        self.assertContains(response, "112", status_code=200)


class MyPollTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_poll(question="question1", days=-5, vtype=1)
        create_poll(
            question="question2",
            username="user2",
            email="user2@example.com",
            days=-5,
            vtype=1,
        )

    def test_redirect_when_not_logged_in(self):
        """
        If the user is not logged in then redirect to the login page
        """
        response = self.client.get(reverse("my_polls"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/my-polls/",
            status_code=302,
            target_status_code=200,
        )

    def test_display_only_user_polls(self):
        """
        Only polls created by the logged in user should be displayed.
        """
        self.client.login(username="user1", email="user1@example.com", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)

        # Get the queryset of polls created by 'user1'
        user_polls = Poll.objects.filter(user__username="user1").order_by("id")

        # Use `transform=str` to compare the string representation of each Poll object
        self.assertQuerySetEqual(
            response.context["latest_poll_list"],
            map(
                repr, user_polls
            ),  # Use `map(repr, queryset)` to get the expected format
            transform=repr,  # Ensure the actual queryset is transformed to its string representation for comparison
        )


class PollCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user("test", "test@example.com", "test")
        self.client.login(username="test", password="test")

    def test_create_page_exists(self):
        """
        The create a poll form exists.
        """
        response = self.client.post("/create/")
        self.assertEqual(response.status_code, 200)

    def test_create_shows_iframe_code(self):
        """
        Creating a new poll shows a HTML snippet to embed the new poll
        with an iframe.
        """
        poll_data = {
            "question": "Create poll.",
            "choice1": "Choice 1.",
            "radio-poll-type": "1",
            "token-tags": "",
        }
        response = self.client.post("/create/", poll_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "embed_instructions.html")
        self.assertEqual("/1" in response.context["link"], True)

    def test_create_with_no_question(self):
        """
        No question should return an error message.
        """
        response = self.client.post("/create/", {"choice1": "Choice 1."}, follow=True)
        self.assertContains(response, "The question is missing", status_code=200)

    def test_create_with_blank_question(self):
        """
        Blank question should return an error message.
        """
        response = self.client.post(
            "/create/",
            {"question": "", "choice1": "Choice 1."},
            follow=True,
        )
        self.assertContains(response, "The question is missing", status_code=200)

    def test_create_skips_blank_choices(self):
        """
        A blank choice doesn't appear in the poll (but later ones do)
        """
        poll_data = {
            "question": "Create poll.",
            "choice1": "",
            "choice2": "Choice 2.",
            "radio-poll-type": "1",
            "token-tags": "",
        }
        self.client.post("/create/", poll_data, follow=True)
        response = self.client.get("/1/", follow=True)
        self.assertContains(response, "Create poll.", status_code=200)
        self.assertNotContains(response, "Choice 1.")
        self.assertContains(response, "Choice 2.")
        self.assertContains(response, "See Results")


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "user1", "user1ces@gmail.com", "password123"
        )
        self.client.login(username="user1", password="password123")

    def test_user_profile_contains_correct_info(self):
        response = self.client.get(reverse("my_info"))
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the user's information
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

        # Check if date_joined is present (we don't need to check the exact format)
        self.assertContains(response, self.user.date_joined.strftime("%Y"))
        self.assertContains(response, self.user.date_joined.strftime("%B"))

    def test_user_profile_polls_count(self):
        response = self.client.get(reverse("my_info"))
        self.assertEqual(response.status_code, 200)

        # Initially, the user should have 0 polls
        content = response.content.decode("utf-8")
        self.assertRegex(
            content,
            r'<dt class="col-sm-3">Elections created:</dt>\s*<dd class="col-sm-9">\s*<a href="/my-polls/">0</a>',
        )

        # Create a poll
        Poll.objects.create(
            question="Which is your favorite color?",
            pub_date=timezone.now(),
            user=self.user,
            vtype=2,
        )

        # Check again, now the user should have 1 poll
        response = self.client.get(reverse("my_info"))
        content = response.content.decode("utf-8")
        self.assertRegex(
            content,
            r'<dt class="col-sm-3">Elections created:</dt>\s*<dd class="col-sm-9">\s*<a href="/my-polls/">1</a>',
        )

    def test_user_profile_links(self):
        response = self.client.get(reverse("my_info"))
        self.assertEqual(response.status_code, 200)

        # Check if the necessary links are present
        self.assertContains(response, reverse("my_polls"))
        self.assertContains(response, "/accounts/password/change")


class UpdatePollTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create user and log in
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="test"
        )
        self.client.login(username="user1", password="test")

        # Create poll and choices
        self.poll = Poll.objects.create(
            question="Create Sample Poll.",
            pub_date=timezone.now(),
            close_date=timezone.now() + datetime.timedelta(days=10),
            vtype=2,  # Assuming this is the type that uses user authentication
            user=self.user,
        )
        self.choice1 = self.poll.choice_set.create(choice_text="Choice 1.")
        self.choice2 = self.poll.choice_set.create(choice_text="Choice 2.")

        # Simulate voting
        ballot = Ballot.objects.create(
            poll=self.poll,
            user=self.user,
        )
        Vote.objects.create(ballot=ballot, choice=self.choice1)

        # Assuming checked_choices are stored in context based on user votes

    def test_poll_details_show_update_button(self):
        response = self.client.get(reverse("detail", args=(self.poll.id,)))
        self.assertContains(response, "Update Vote", status_code=200)

    def test_poll_details_show_checked_choices(self):
        response = self.client.get(reverse("detail", args=(self.poll.id,)))
        self.assertQuerySetEqual(
            response.context["checked_choices"],
            [self.choice1],
            transform=lambda x: x,  # Directly compare objects
        )
        self.assertContains(response, "Choice 1.", status_code=200)

    def test_poll_details_logout_current_user(self):
        self.client.logout()
        response = self.client.get("/1/")
        self.assertContains(response, "Login to Vote", status_code=200)
        self.assertQuerySetEqual(response.context["checked_choices"], [])

    def test_poll_details_different_user(self):
        self.client.logout()
        User.objects.create_user("user2", "user2@example.com", "password123")
        self.client.login(
            username="user2",
            email="user2@example.com",
            password="password123",
        )
        response = self.client.get("/1/")
        self.assertContains(response, "Vote", status_code=200)
        self.assertQuerySetEqual(response.context["checked_choices"], [])

    def test_poll_details_unselect_checked_choice(self):
        self.client.login(username="user1", email="user1@example.com", password="test")
        choice_data = {}
        self.client.post("/1/vote/", choice_data, follow=True)
        response = self.client.get("/1/")
        self.assertContains(response, "Vote", status_code=200)
        self.assertQuerySetEqual(response.context["checked_choices"], [])

    def test_poll_details_closed_poll(self):
        poll_closed = create_poll(
            question="Create Closed Poll.",
            username="user2",
            email="user2@example.com",
            close_date=timezone.now() + datetime.timedelta(days=-10),
        )
        self.client.login(
            username="user2",
            email="user2@example.com",
            password="password123",
        )
        response = self.client.get(reverse("detail", args=(poll_closed.id,)))
        self.assertContains(response, "Sorry! This poll is closed.", status_code=200)


class DeletePollTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_poll(question="question1", days=-5, vtype=1)
        poll = Poll.objects.create(
            question="question2",
            pub_date=timezone.now() + datetime.timedelta(days=-10),
            user=User.objects.get(username="user1"),
            vtype=2,
            close_date=None,
        )

        for _ in range(2):
            create_ballot(poll)
        self.client.login(username="user1", email="user1@example.com", password="test")

    def test_delete_one_poll(self):
        self.client.delete("/1/delete", follow=True)
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)

        # Assuming 'latest_poll_list' is a Page object from pagination
        # Extract the list of Poll objects from the Page object
        actual_polls = list(response.context["latest_poll_list"].object_list)

        # Create a list of the expected Poll objects' string representations
        expected_polls = Poll.objects.filter(question="question2")
        expected_strings = [str(poll) for poll in expected_polls]

        # Compare the actual list of Poll objects (converted to their string representations) with the expected strings
        self.assertListEqual(
            [str(poll) for poll in actual_polls],
            # Convert each Poll object in the actual list to its string representation
            expected_strings,
        )

        response = self.client.get("/1/")
        self.assertEqual(response.status_code, 404)

    def test_delete_all_polls(self):
        self.client.delete("/1/delete", follow=True)
        self.client.delete("/2/delete", follow=True)
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["latest_poll_list"], [])
        response = self.client.get("/1/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/2/")
        self.assertEqual(response.status_code, 404)


class PollVisibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username="user1", email="user1@example.com", password="test")
        self.public_poll = create_poll(
            question="public poll", days=-10, vtype=3, ballots=2, is_private=False
        )

        user2 = User.objects.create_user("user2", "user2@example.com", "test")
        self.private_poll = Poll.objects.create(
            question="private poll",
            pub_date=timezone.now() + datetime.timedelta(days=-10),
            user=user2,
            vtype=3,
            is_private=True,
        )
        create_ballot(self.private_poll)

    def test_public_poll(self):
        """
        A poll that is marked public should appear on the home page, and
        a private one should not.
        """
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["latest_poll_list"],
            [repr(self.public_poll)],
            transform=repr,
        )

    def test_private_poll(self):
        """
        A poll that is marked private is visible to its owner, along with
        his/her public polls.
        """
        self.client.logout()
        self.client.login(username="user2", email="user2@example.com", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["latest_poll_list"],
            [repr(self.private_poll)],
            transform=repr,
        )

    def test_private_poll_different_user(self):
        """
        A poll that is marked private should not be visible to another user.
        """
        self.client.logout()
        self.client.login(username="user1", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["latest_poll_list"],
            [repr(self.public_poll)],
            transform=repr,
        )


class TagCloudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = create_poll(
            question="Create Sample Poll.",
            close_date=timezone.now() + datetime.timedelta(days=3),
            vtype=1,
        )
        self.poll.choice_set.create(choice_text="Choice 1.")
        self.poll.add_tags(["New York"])
        self.choice = Choice.objects.get(poll_id=self.poll.id)
        self.client.login(username="user1", email="user1@example.com", password="test")

    def test_poll_tag_exists(self):
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/tag/new%20york/")
        self.assertContains(response, "new york")

    def test_poll_tags_index(self):
        # print [pt.tag_text for pt in self.poll.polltag_set.all()]
        response = self.client.get(reverse("tagged_polls", args=("New York",)))
        self.assertEqual(response.status_code, 200)
        print(response.content)
        self.assertContains(response, '<a href="/1/">Create Sample Poll.</a>')

    def test_poll_delete(self):
        self.poll.polltag_set.clear()
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<a href='/tag/new%20york/'")
        self.assertNotContains(response, "new york")


class VoteInvitationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "poll_creator", "creator@example.com", "password123"
        )
        self.voter_email = "voter@example.com"
        self.poll = create_poll(
            question="Invitation Test Poll",
            username="poll_creator",
            email="creator@example.com",
            days=-5,
            vtype=3,
        )
        self.choice1 = self.poll.choice_set.create(choice_text="Choice 1")
        self.choice2 = self.poll.choice_set.create(choice_text="Choice 2")

    def test_create_invitation(self):
        """Test creating a vote invitation"""
        invitation = create_vote_invitation(self.poll, self.voter_email)
        self.assertEqual(invitation.email, self.voter_email)
        self.assertEqual(invitation.poll, self.poll)
        self.assertIsNotNone(invitation.key)

    def test_send_vote_invitations(self):
        """Test Poll.send_vote_invitations creates invitations"""
        emails = "voter1@example.com, voter2@example.com, voter3@example.com"
        invitations = self.poll.send_vote_invitations(emails)
        self.assertEqual(len(invitations), 3)
        self.assertEqual(
            set(inv.email for inv in invitations),
            {"voter1@example.com", "voter2@example.com", "voter3@example.com"},
        )

    def test_send_vote_invitations_filters_invalid_emails(self):
        """Test that invalid emails are filtered out"""
        emails = "valid@example.com, invalid-email, another@example.com, not-an-email"
        invitations = self.poll.send_vote_invitations(emails)
        self.assertEqual(len(invitations), 2)
        emails_list = [inv.email for inv in invitations]
        self.assertIn("valid@example.com", emails_list)
        self.assertIn("another@example.com", emails_list)
        self.assertNotIn("invalid-email", emails_list)

    def test_invited_emails(self):
        """Test Poll.invited_emails returns correct list"""
        create_vote_invitation(self.poll, "voter1@example.com")
        create_vote_invitation(self.poll, "voter2@example.com")
        invited = self.poll.invited_emails()
        self.assertEqual(len(invited), 2)
        self.assertIn("voter1@example.com", invited)
        self.assertIn("voter2@example.com", invited)

    def test_get_invitation_url(self):
        """Test VoteInvitation.get_invitation_url generates correct URL"""
        invitation = create_vote_invitation(self.poll, self.voter_email)
        # Generate a proper key
        invitation.key = VoteInvitation.generate_key()
        invitation.save()

        url = invitation.get_invitation_url()
        self.assertIn(str(self.poll.id), url)
        self.assertIn(invitation.key, url)
        self.assertIn(self.voter_email, url)

    def test_vote_with_invitation_link(self):
        """Test voting via invitation link creates and links ballot"""
        invitation = create_vote_invitation(self.poll, self.voter_email)
        invitation.key = VoteInvitation.generate_key()
        invitation.save()

        # Vote via invitation link
        response = self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {
                "invitation_key": invitation.key,
                "invitation_email": self.voter_email,
                "choice1": "",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check ballot was created and linked
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.ballot)
        self.assertEqual(invitation.ballot.email, self.voter_email)

    def test_vote_with_invitation_updates_existing_ballot(self):
        """Test that voting again with same invitation updates existing ballot"""
        invitation = create_vote_invitation(self.poll, self.voter_email)
        invitation.key = VoteInvitation.generate_key()
        invitation.save()

        # First vote
        self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {
                "invitation_key": invitation.key,
                "invitation_email": self.voter_email,
                "choice1": "",
            },
        )

        # Second vote with different choice
        response = self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {
                "invitation_key": invitation.key,
                "invitation_email": self.voter_email,
                "choice2": "",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check same ballot was used
        invitation.refresh_from_db()
        ballot_id = invitation.ballot.id
        invitation.refresh_from_db()
        self.assertEqual(invitation.ballot.id, ballot_id)

    def test_vote_without_invitation_fails(self):
        """Test that voting without valid invitation fails for vtype=3"""
        response = self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {"choice1": ""},
            follow=True,
        )
        # Should redirect back to detail page with error
        self.assertEqual(response.status_code, 200)

    def test_detail_view_with_invitation_link(self):
        """Test detail view shows voting form when accessed via invitation link"""
        invitation = create_vote_invitation(self.poll, self.voter_email)
        invitation.key = VoteInvitation.generate_key()
        invitation.save()

        url = reverse("invitation", args=(self.poll.id,))
        url += f"?key={invitation.key}&email={self.voter_email}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["vote_authorized"])
        self.assertEqual(response.context["vote_invitation"], invitation)

    def test_detail_view_without_invitation_unauthorized(self):
        """Test detail view shows unauthorized message for vtype=3 without invitation"""
        response = self.client.get(reverse("detail", args=(self.poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("vote_authorized", False))

    def test_authenticated_user_with_invited_email_can_vote(self):
        """Test authenticated user with invited email can vote"""
        invited_user = User.objects.create_user(
            "invited_user", self.voter_email, "password123"
        )
        create_vote_invitation(self.poll, self.voter_email)

        self.client.login(username="invited_user", password="password123")
        response = self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {"invitation_email": self.voter_email, "choice1": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check ballot was created and linked to invitation
        invitation = VoteInvitation.objects.get(email=self.voter_email, poll=self.poll)
        self.assertIsNotNone(invitation.ballot)
        self.assertEqual(invitation.ballot.user, invited_user)

    def test_authenticated_user_not_invited_cannot_vote(self):
        """Test authenticated user without invitation cannot vote"""
        User.objects.create_user("non_invited", "notinvited@example.com", "password123")
        self.client.login(username="non_invited", password="password123")

        response = self.client.post(
            reverse("vote", args=(self.poll.id,)),
            {"invitation_email": "notinvited@example.com", "choice1": ""},
            follow=True,
        )
        # Should redirect with error message
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(any("not invited" in str(m).lower() for m in messages))

    def test_poll_admin_shows_invitations(self):
        """Test poll admin page shows invitations for vtype=3 polls"""
        create_vote_invitation(self.poll, "voter1@example.com")
        create_vote_invitation(self.poll, "voter2@example.com")

        self.client.login(username="poll_creator", password="password123")
        response = self.client.get(reverse("poll_admin", args=(self.poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["invitations"]), 2)
        self.assertContains(response, "voter1@example.com")
        self.assertContains(response, "voter2@example.com")

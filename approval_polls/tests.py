import datetime

import structlog
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from approval_polls.models import Ballot, Choice, Poll, Vote

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
        self.assertContains(response, "(page 1 of 1)", status_code=200)


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
        self.assertContains(response, "0 votes (0%)", status_code=200)

    def test_results_view_with_ballots(self):
        """
        Results page of a poll with a choice and ballots shows the correct
        percentage, total vote count, and total ballot count.
        """
        poll = create_poll(question="Choice poll.", ballots=1)
        choice = poll.choice_set.create(choice_text="Choice text.")
        create_ballot(poll).vote_set.create(choice=choice)
        response = self.client.get(reverse("results", args=(poll.id,)))
        self.assertContains(response, "1 vote (50%)", status_code=200)


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
        self.assertTrue("/1" in response.context["link"])

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
        User.objects.create_user("user1", "user1ces@gmail.com", "password123")
        self.client.login(
            username="user1", email="user1@example.com", password="password123"
        )

    def test_user_profile_member_since(self):
        response = self.client.get(reverse("my_info"))
        stored_date = User.objects.get(username="user1").date_joined
        desired_date = timezone.localtime(stored_date)
        test_user_date_joined = desired_date.strftime("%B %d, %Y").replace(" 0", " ")
        self.assertContains(response, "Member since: " + str(test_user_date_joined))

    def test_user_profile_last_login(self):
        response = self.client.get(reverse("my_info"))
        stored_date = User.objects.get(username="user1").last_login
        desired_date = timezone.localtime(stored_date)
        test_user_last_login = desired_date.strftime("%B %d, %Y").replace(" 0", " ")
        self.assertContains(response, "Last Login: " + str(test_user_last_login))

    def test_show_polls_created_no_polls(self):
        response = self.client.get(reverse("my_info"))
        html_string = '<p><a href="/my-polls/">Polls I created</a>: 0</p>'
        self.assertContains(response, html_string, html=True)

    def test_show_polls_created_one_poll(self):
        poll = Poll.objects.create(
            question="Which is your favorite color?",
            pub_date=timezone.now() + datetime.timedelta(days=0),
            user=User.objects.get(username="user1"),
            vtype=2,
        )

        for _ in range(0):
            create_ballot(poll)

        response = self.client.get(reverse("my_info"))
        html_string = '<p><a href="/my-polls/">Polls I created</a>: 1</p>'
        self.assertContains(response, html_string, html=True)


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
            username="user2", email="user2@example.com", password="password123"
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
            username="user2", email="user2@example.com", password="password123"
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
        self.client.delete("/1/", follow=True)
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
        self.client.delete("/1/", follow=True)
        self.client.delete("/2/", follow=True)
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
            response.context["latest_poll_list"], [repr(self.public_poll)], transform=repr
        )


class PollEditTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.poll = create_poll(
            question="Create Sample Poll.",
            close_date=timezone.now() + datetime.timedelta(days=3),
            vtype=3,
        )
        self.client.login(username="user1", password="test")

        create_vote_invitation(self.poll, email="test1@test1.com")
        self.choice = self.poll.choice_set.create(choice_text="Choice 1.")

    def test_edit_view_with_invalid_poll(self):
        """
        Requesting the edit page of a non-existent poll should
        return a 404 not found error.
        """
        response = self.client.get(reverse("edit", args=(10000,)))
        self.assertEqual(response.status_code, 404)

    def test_edit_view_visible_to_other_user(self):
        """
        The edit page of a poll belonging to one user should not be
        visible to another user. It should return a permission denied (403) error.
        """
        User.objects.create_user("user2", "user2@example.com", "test")
        self.client.logout()
        self.client.login(username="user2", password="test")
        response = self.client.get(reverse("edit", args=(self.poll.id,)))
        self.assertEqual(response.status_code, 403)

    def test_email_invitees_are_returned(self):
        """
        The poll's edit page should list email invitees if poll.vtype is 3
        """
        response = self.client.get(reverse("edit", args=(self.poll.id,)))
        self.assertEqual(response.context["invited_emails"], "test1@test1.com")

    def test_new_choices_are_added(self):
        """
        New choices should be added to the poll and existing ones should be updated.
        """
        self.client.post(
            reverse("edit", args=(self.poll.id,)),
            {
                "choice1": "xxx",
                "linkurl-choice1": "xxx",
                "choice1000": "BBBBB",
                "linkurl-choice1000": "BBBBBBBB",
                "close-datetime": "bb",
                "question": "q",
                "token-tags": "",
            },
        )

        # Refresh poll and choice objects from the database
        self.poll.refresh_from_db()
        self.choice.refresh_from_db()

        # Check if the existing choice was updated
        self.assertEqual(self.choice.choice_text, "xxx")

        # Check if the new choice was added
        new_choice = self.poll.choice_set.get(choice_text="BBBBB")
        self.assertIsNotNone(new_choice)
        self.assertEqual(new_choice.choice_text, "BBBBB")

        # Verify the response contains the expected HTML elements
        response = self.client.get(reverse("edit", args=(self.poll.id,)))

        logger.info(response.content)

        self.assertContains(
            response,
            "<span class='glyphicon glyphicon-link text-success'>",
            None,
            200,
            "",
            html=True,
        )

    def test_can_not_edit_poll(self):
        """
        If ballots are on the poll, editing should not happen
        """
        create_ballot(self.poll)
        response = self.client.get(reverse("edit", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["can_edit_poll"], False)
        self.assertContains(
            response,
            "You cannot edit the questions and choices as this poll has got ballots on it!",
        )
        self.client.post(
            reverse("edit", args=(1,)),
            {
                "choice1": "xxx",
                "linkurl-choice1": "xxx",
                "choice1000": "BBBBB",
                "linkurl-choice1000": "BBBBBBBB",
                "close-datetime": "bb",
                "question": "q",
                "token-tags": "",
            },
        )
        self.assertEqual(Poll.objects.get(id=self.poll.id).choice_set.count(), 1)
        self.assertEqual(Choice.objects.get(id=self.choice.id).choice_text, "Choice 1.")


# class SuspendPollTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.poll = create_poll(
#             question="Create Sample Poll.",
#             close_date=timezone.now() + datetime.timedelta(days=3),
#             vtype=3,
#             is_suspended=True,
#         )
#         self.poll.choice_set.create(choice_text="Choice 1.")
#         self.choice = Choice.objects.get(poll_id=self.poll.id)
#         self.client.login(username="user1", email="user1@example.com", password="test")

#     def test_suspend_tests(self):
#         response = self.client.get(reverse("my_polls"))
#         self.assertEqual(response.status_code, 200)

#         # Debugging: print response content
#         print(response.content.decode())

#         self.assertContains(response, "id='unsuspend-poll-1'> unsuspend </a>")

#         # Unsuspend the poll and check again
#         self.poll.is_suspended = False
#         self.poll.save()

#         response = self.client.get(reverse("my_polls"))

#         # Debugging: print response content
#         print(response.content.decode())

#         self.assertContains(response, "id='suspend-poll-1'> suspend </a>")

#     def test_suspended_tests_cannot_vote(self):
#         response = self.client.get(reverse("detail", args=(self.poll.id,)))
#         self.assertEqual(response.status_code, 200)

#         # Debugging: print response content
#         print(response.content.decode())

#         self.assertContains(
#             response, "Sorry! This poll has been temporarily suspended."
#         )
#         self.assertContains(
#             response,
#             "<button class='btn btn-success' type='submit' disabled>Vote</button>",
#             html=True,
#         )


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
        self.assertContains(response, "<a href='/tag/new%20york/'>new york</a>")

    def test_poll_tags_index(self):
        # print [pt.tag_text for pt in self.poll.polltag_set.all()]
        response = self.client.get(reverse("tagged_polls", args=("New York",)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/1/">Create Sample Poll.</a>')

    def test_poll_delete(self):
        self.poll.polltag_set.clear()
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<a href='/tag/new%20york/'>new york</a>")

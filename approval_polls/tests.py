import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from approval_polls.forms import RegistrationFormCustom
from approval_polls.models import Choice, Poll, Subscription


class UserLoginTests(TestCase):
    """
    This class tests for user login validations.

    """

    errorString = "Invalid credentials. Please try again."

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user("user1", "user1@example.com", "user1Password")
        user.save()

    def login_user(self, username, password):
        """
        Helper method for user login. Validates both response and login status.

        """
        response = self.client.post(
            "/accounts/login/",
            data={"username": username, "password": password},
            follow=True,
        )
        status = self.client.login(username=username, password=password)
        return response, status

    def test_invalid_username_password(self):
        """
        Test login with an incorrect username and password combination.

        """
        response, status = self.login_user("user1", "invalid")
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)

    def test_invalid_email_password(self):
        """
        Test login with an incorrect email and password combination.

        """
        response, status = self.login_user("user1@example.com", "invalid")
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)

    def test_valid_username_password(self):
        """
        Test login with a correct username and password combination.

        """
        response, status = self.login_user("user1", "user1Password")
        self.assertNotContains(response, self.errorString, status_code=200)
        self.assertTrue(status)

    def test_valid_email_password(self):
        """
        Test login with a correct email and password combination.

        """
        response, status = self.login_user("user1@example.com", "user1Password")
        self.assertNotContains(response, self.errorString, status_code=200)
        self.assertTrue(status)

    def test_non_existent_username(self):
        """
        Test login with a non-existent username.

        """
        response, status = self.login_user("user2", "user1Password")
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)

    def test_non_existent_email(self):
        """
        Test login with a non-existent email.

        """
        response, status = self.login_user("user2@example.com", "user1Password")
        self.assertContains(response, self.errorString, status_code=200)
        self.assertFalse(status)


class RegistrationFormCustomTests(TestCase):
    """
    This class tests the custom registration form functionality.

    """

    def test_registration_form_custom(self):
        """
        Test that `RegistrationFormCustom` enforces custom username
        constraints during registration.

        """
        invalid_data_dicts = [
            {
                # Username with '@' is invalid.
                "data": {
                    "username": "foo@somedomain.com",
                    "email": "foo@example.com",
                    "password1": "foo",
                    "password2": "foo",
                },
                "error": (
                    "username",
                    [
                        "This value may contain only letters, numbers and ./+/-/_ characters."
                    ],
                ),
            },
        ]

        for invalid_dict in invalid_data_dicts:
            form = RegistrationFormCustom(data=invalid_dict["data"])
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors[invalid_dict["error"][0]], invalid_dict["error"][1]
            )


class ChangeUsernameTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user("user2", "user2ces@gmail.com", "password123")
        self.client.login(username="user2", password="password123")

    def test_username_change_error_empty(self):
        """
        New Username Field is Empty
        """
        username_data = {"new_username": ""}
        response = self.client.post(
            "/accounts/username/change/", username_data, follow=True
        )
        html_string = "This field is required."
        self.assertContains(response, html_string)

    def test_username_change_illegal_chars_error(self):
        """
        New Username contains '@'
        """
        username_data = {"new_username": "user@1987"}
        response = self.client.post(
            "/accounts/username/change/", username_data, follow=True
        )
        html_string = (
            "This value may contain only letters, numbers and ./+/-/_ characters."
        )
        self.assertContains(response, html_string)

    def test_username_change_maxlen_error(self):
        """
        New Username is longer than 30 characters
        """
        username_data = {"new_username": "kuhhahheriqwemniackolaxcivjkleqwerty"}
        response = self.client.post(
            "/accounts/username/change/", username_data, follow=True
        )
        html_string = "Ensure this value has at most 30 characters (it has 36)."
        self.assertContains(response, html_string)

    def test_username_change_already_exists(self):
        """
        New Username is already registered
        """
        User.objects.create_user("usertest", "usertestces@gmail.com", "password123")
        username_data = {"new_username": "usertest"}
        response = self.client.post(
            "/accounts/username/change/", username_data, follow=True
        )
        html_string = "A user with that username already exists."
        self.assertContains(response, html_string)

    def test_username_change_success(self):
        """
        Username was successfully changed
        """
        username_data = {"new_username": "user1987"}
        response = self.client.post(
            "/accounts/username/change/", username_data, follow=True
        )
        html_string = "Your Username was changed to user1987."
        self.assertContains(response, html_string)


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user("user3", "user3ces@gmail.com", "password123")
        self.client.login(username="user3", password="password123")

    def test_password_change_error_empty(self):
        """
        Password Fields are Empty
        """
        password_data = {"old_password": "", "new_password1": "", "new_password2": ""}
        response = self.client.post(
            "/accounts/password/change/", password_data, follow=True
        )
        html_string = "This field is required."
        self.assertContains(response, html_string)

    def test_password_change_old_pass_error(self):
        """
        Old Password did not match the records
        """
        password_data = {
            "old_password": "password1",
            "new_password1": "password123",
            "new_password2": "password123",
        }
        response = self.client.post(
            "/accounts/password/change/", password_data, follow=True
        )
        html_string = "Your old password was entered incorrectly."
        self.assertContains(response, html_string)

    def test_password_change_no_match_error(self):
        """
        New Passwords did not match
        """
        password_data = {
            "old_password": "password123",
            "new_password1": "password123",
            "new_password2": "password124",
        }
        response = self.client.post(
            "/accounts/password/change/", password_data, follow=True
        )
        html_string = '<label class="control-label" for="id_new_password2">The two password fields \
        didn&39;t match.</label>'
        self.assertContains(response, html_string, html=True)

    def test_password_change_success(self):
        """
        Password was successfully changed
        """
        password_data = {
            "old_password": "password123",
            "new_password1": "password1234",
            "new_password2": "password1234",
        }
        response = self.client.post(
            "/accounts/password/change/", password_data, follow=True
        )
        html_string = "Your Password was changed."
        self.assertContains(response, html_string)


class UserSubscriptions(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("user1", "test1@gmail.com", "user1")
        self.user.save()
        self.client.login(username="user1", password="user1")

    def test_user_unsubscribed_by_default(self):
        """
        User is unsubscribed by default
        """
        response = self.client.get("/accounts/subscription/change/")
        self.assertContains(
            response,
            "<input type='checkbox' id='id_newslettercheckbox' name='newslettercheckbox' >",
            html=True,
        )

    def test_user_subcribed(self):
        """
        User subscribes to newsletter
        """
        self.client.post(
            "/accounts/subscription/change/",
            {"newslettercheckbox": ["on"], "zipcode": ["60660"]},
        )
        response = self.client.get("/accounts/subscription/change/")
        self.assertContains(
            response,
            "<input type='checkbox' id='id_newslettercheckbox' name='newslettercheckbox' checked>",
            html=True,
        )
        sub = Subscription.objects.filter(user=self.user)
        self.assertEqual(sub.count(), 1)

    def test_subscribed_user_unsubscribed(self):
        """
        User unsubscribes from newsletter
        """
        Subscription(user=self.user, zipcode="60660").save()
        self.client.post("/accounts/subscription/change/", {})
        response = self.client.get("/accounts/subscription/change/")
        self.assertContains(
            response,
            "<input type='checkbox' id='id_newslettercheckbox' name='newslettercheckbox' >",
            html=True,
        )
        sub = Subscription.objects.filter(user=self.user)
        self.assertEqual(sub.count(), 0)


def create_poll(
    question,
    username="user1",
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
        self.assertQuerysetEqual(response.context["latest_poll_list"], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the
        index page.
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse("index"))
        self.assertQuerysetEqual(
            response.context["latest_poll_list"], ["<Poll: Past poll.>"]
        )

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be
        displayed.
        """
        create_poll(question="Past poll.", days=-30, vtype=1)
        create_poll(question="Future poll.", username="user2", days=30, vtype=1)
        response = self.client.get(reverse("index"))
        self.assertQuerysetEqual(
            response.context["latest_poll_list"], ["<Poll: Past poll.>"]
        )

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page may display multiple polls.
        """
        create_poll(question="Past poll 1.", days=-30)
        create_poll(question="Past poll 2.", username="user2", days=-5)
        response = self.client.get(reverse("index"))
        self.assertQuerysetEqual(
            response.context["latest_poll_list"],
            ["<Poll: Past poll 2.>", "<Poll: Past poll 1.>"],
        )

    def test_index_view_with_empty_page(self):
        """
        If an empty page of polls is requested, then the last page of
        polls is returned.
        """
        create_poll(question="Empty page poll.")
        response = self.client.get("/approval_polls/?page=2")
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
        self.assertContains(response, "0 votes on 0", status_code=200)

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
        self.assertContains(response, "1 vote on 2", status_code=200)


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
        for _ in range(10):
            create_ballot(poll).vote_set.create(choice=choice2)
        response = self.client.post(
            "/approval_polls/" + str(poll.id) + "/vote/",
            data={"choice2": ""},
            follow=True,
        )
        self.assertContains(response, "10 votes")
        self.assertContains(response, "21 votes")
        self.assertContains(response, "101", status_code=200)


class MyPollTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_poll(question="question1", days=-5, vtype=1)
        create_poll(question="question2", username="user2", days=-5, vtype=1)

    def test_redirect_when_not_logged_in(self):
        """
        If the user is not logged in then redirect to the login page
        """
        response = self.client.get(reverse("my_polls"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/approval_polls/my-polls/",
            status_code=302,
            target_status_code=200,
        )

    def test_display_only_user_polls(self):
        """
        Only polls created by the logged in user should be displayed.
        """
        self.client.login(username="user1", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_poll_list"], ["<Poll: question1>"]
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
        response = self.client.post("/approval_polls/create/")
        self.assertEquals(response.status_code, 200)

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
        response = self.client.post("/approval_polls/create/", poll_data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "approval_polls/embed_instructions.html")
        self.assertTrue("/approval_polls/1" in response.context["link"])

    def test_create_with_no_question(self):
        """
        No question should return an error message.
        """
        response = self.client.post(
            "/approval_polls/create/", {"choice1": "Choice 1."}, follow=True
        )
        self.assertContains(response, "The question is missing", status_code=200)

    def test_create_with_blank_question(self):
        """
        Blank question should return an error message.
        """
        response = self.client.post(
            "/approval_polls/create/",
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
        self.client.post("/approval_polls/create/", poll_data, follow=True)
        response = self.client.get("/approval_polls/1/", follow=True)
        self.assertContains(response, "Create poll.", status_code=200)
        self.assertNotContains(response, "Choice 1.")
        self.assertContains(response, "Choice 2.")
        self.assertContains(response, "See Results")


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user("user1", "user1ces@gmail.com", "password123")
        self.client.login(username="user1", password="password123")

    def test_user_profile_show_username(self):
        """
        The User Profile page should show the following text:

        My User Profile (user1)
        """
        response = self.client.get(reverse("my_info"))
        self.assertContains(response, "My User Profile (user1)")

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
        html_string = (
            '<p><a href="/approval_polls/my-polls/">Polls I created</a>: 0</p>'
        )
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
        html_string = (
            '<p><a href="/approval_polls/my-polls/">Polls I created</a>: 1</p>'
        )
        self.assertContains(response, html_string, html=True)


class UpdatePollTests(TestCase):
    def setUp(self):
        self.client = Client()
        poll = create_poll(
            question="Create Sample Poll.",
            close_date=timezone.now() + datetime.timedelta(days=10),
        )
        poll.choice_set.create(choice_text="Choice 1.")
        self.client.login(username="user1", password="test")
        choice_data = {
            "choice1": "on",
        }
        self.client.post("/approval_polls/1/vote/", choice_data, follow=True)

    def test_poll_details_show_update_button(self):
        response = self.client.get("/approval_polls/1/")
        self.assertContains(response, "Update Vote", status_code=200)

    def test_poll_details_show_checked_choices(self):
        response = self.client.get("/approval_polls/1/")
        self.assertQuerysetEqual(
            response.context["checked_choices"], ["<Choice: Choice 1.>"]
        )

    def test_poll_details_logout_current_user(self):
        self.client.logout()
        response = self.client.get("/approval_polls/1/")
        self.assertContains(response, "Login to Vote", status_code=200)
        self.assertQuerysetEqual(response.context["checked_choices"], [])

    def test_poll_details_different_user(self):
        self.client.logout()
        User.objects.create_user("user2", "user2@example.com", "password123")
        self.client.login(username="user2", password="password123")
        response = self.client.get("/approval_polls/1/")
        self.assertContains(response, "Vote", status_code=200)
        self.assertQuerysetEqual(response.context["checked_choices"], [])

    def test_poll_details_unselect_checked_choice(self):
        self.client.login(username="user1", password="test")
        choice_data = {}
        self.client.post("/approval_polls/1/vote/", choice_data, follow=True)
        response = self.client.get("/approval_polls/1/")
        self.assertContains(response, "Vote", status_code=200)
        self.assertQuerysetEqual(response.context["checked_choices"], [])

    def test_poll_details_closed_poll(self):
        poll_closed = create_poll(
            question="Create Closed Poll.",
            username="user2",
            close_date=timezone.now() + datetime.timedelta(days=-10),
        )
        self.client.login(username="user2", password="password123")
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
        self.client.login(username="user1", password="test")

    def test_delete_one_poll(self):
        self.client.delete("/approval_polls/1/", follow=True)
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_poll_list"], ["<Poll: question2>"]
        )
        response = self.client.get("/approval_polls/1/")
        self.assertEqual(response.status_code, 404)

    def test_delete_all_polls(self):
        self.client.delete("/approval_polls/1/", follow=True)
        self.client.delete("/approval_polls/2/", follow=True)
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_poll_list"], [])
        response = self.client.get("/approval_polls/1/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/approval_polls/2/")
        self.assertEqual(response.status_code, 404)


class PollVisibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username="user1", password="test")
        create_poll(
            question="public poll", days=-10, vtype=3, ballots=2, is_private=False
        )
        poll = Poll.objects.create(
            question="private poll",
            pub_date=timezone.now() + datetime.timedelta(days=-10),
            user=User.objects.get(username="user1"),
            vtype=3,
            is_private=True,
        )
        for _ in range(2):
            create_ballot(poll)
        User.objects.create_user("user2", "user2@example.com", "test")

    def test_public_poll(self):
        """
        A poll that is marked public should appear on the home page, and
        a private one should not.
        """
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_poll_list"],
            ["<Poll: public poll>"],
        )

    def test_private_poll(self):
        """
        A poll that is marked private is visible to its owner, along with
        his/her public polls.
        """
        self.client.login(username="user1", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_poll_list"],
            ["<Poll: private poll>", "<Poll: public poll>"],
        )

    def test_private_poll_different_user(self):
        """
        A poll that is marked private should not be visible to another user.
        """
        self.client.logout()
        self.client.login(username="user2", password="test")
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["latest_poll_list"],
            [],
        )


class PollEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = create_poll(
            question="Create Sample Poll.",
            close_date=timezone.now() + datetime.timedelta(days=3),
            vtype=3,
        )
        create_vote_invitation(self.poll, email="test1@test1.com")
        self.poll.choice_set.create(choice_text="Choice 1.")
        self.choice = Choice.objects.get(poll_id=self.poll.id)
        self.client.login(username="user1", password="test")

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
        response = self.client.get(reverse("edit", args=(1,)))
        self.assertEqual(response.status_code, 403)

    def test_email_invitees_are_returned(self):
        """
        The poll's edit page should list email invitees if poll.vtype is 3
        """
        response = self.client.get(reverse("edit", args=(1,)))
        self.assertEqual(response.context["invited_emails"], "test1@test1.com")

    def test_new_choices_are_added(self):
        """
        New choices should be added in the poll and
        existing should be updated
        """
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
        self.assertEqual(Poll.objects.get(id=self.poll.id).choice_set.count(), 2)
        self.assertEqual(Choice.objects.get(id=self.choice.id).choice_text, "xxx")
        response = self.client.get(reverse("edit", args=(1,)))
        self.assertContains(
            response,
            "<a href='#' class='add-link' id='link-choice1' \
            title='Add link' data-toggle='tooltip' data-placement='bottom'> \
            <span class='glyphicon glyphicon-link text-success' ></span> </a>",
            None,
            200,
            "",
            True,
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


class SuspendPollTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = create_poll(
            question="Create Sample Poll.",
            close_date=timezone.now() + datetime.timedelta(days=3),
            vtype=3,
            is_suspended=True,
        )
        self.poll.choice_set.create(choice_text="Choice 1.")
        self.choice = Choice.objects.get(poll_id=self.poll.id)
        self.client.login(username="user1", password="test")

    def test_suspend_tests(self):
        response = self.client.get(reverse("my_polls"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id='unsuspend-poll-1'> unsuspend </a>")
        self.poll.is_suspended = False
        self.poll.save()
        response = self.client.get(reverse("my_polls"))
        self.assertContains(response, "id='suspend-poll-1'> suspend </a>")

    def test_suspended_tests_cannot_vote(self):
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertContains(
            response, "Sorry! This poll has been temporarily suspended."
        )
        self.assertContains(
            response,
            "<button class='btn btn-success' type='submit'  disabled >Vote</button>",
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
        self.client.login(username="user1", password="test")

    def test_poll_tag_exists(self):
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<a href='/approval_polls/tag/new%20york/'>new york</a>"
        )

    def test_poll_tags_index(self):
        # print [pt.tag_text for pt in self.poll.polltag_set.all()]
        response = self.client.get(reverse("tagged_polls", args=("New York",)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<a href="/approval_polls/1/">Create Sample Poll.</a>'
        )

    def test_poll_delete(self):
        self.poll.polltag_set.clear()
        response = self.client.get(reverse("detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, "<a href='/approval_polls/tag/new%20york/'>new york</a>"
        )

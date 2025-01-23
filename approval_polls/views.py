import datetime
import json
import re

import structlog
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Prefetch
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_http_methods

from approval_polls.models import (
    Ballot,
    Poll,
    PollTag,
    Subscription,
    Vote,
    VoteInvitation,
)

from .forms import ManageSubscriptionsForm, NewUsernameForm

logger = structlog.get_logger(__name__)


@login_required
def changeUsername(request):
    if request.method == "POST":
        form = NewUsernameForm(request.POST)

        if form.is_valid():
            newusername = form.cleaned_data["new_username"]
            owner = request.user
            owner.username = newusername
            owner.save()
            return HttpResponseRedirect("/accounts/username/change/done/")
    else:
        form = NewUsernameForm()

    return render(request, "registration/username_change_form.html", {"form": form})


@login_required
def changeUsernameDone(request):
    return render(
        request,
        "registration/username_change_done.html",
        {"new_username": request.user},
    )


@login_required
def manageSubscriptions(request):
    current_user = request.user
    if request.method == "POST":
        form = ManageSubscriptionsForm(request.POST)
        if form.is_valid():
            zipcode = form.cleaned_data.get("zipcode")
            is_subscribed = form.cleaned_data.get("newslettercheckbox")
            if current_user.subscription_set.count() > 0:
                if not is_subscribed:
                    current_user.subscription_set.first().delete()
            else:
                subscr = Subscription(user=current_user, zipcode=zipcode)
                subscr.save()

            return HttpResponseRedirect("/accounts/subscription/change/done/")
        else:
            is_subscribed = False
    else:
        if current_user.subscription_set.count() > 0:
            subscr = current_user.subscription_set.first()
            form = ManageSubscriptionsForm(
                initial={"user": request.user, "zipcode": subscr.zipcode}
            )
            is_subscribed = True
        else:
            form = ManageSubscriptionsForm()
            is_subscribed = False

    return render(
        request,
        "registration/subscription_preferences.html",
        {"form": form, "boxchecked": is_subscribed},
    )


@login_required
def manageSubscriptionsDone(request):
    return render(
        request,
        "registration/subscription_change_done.html",
        {"new_username": request.user},
    )


def index(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(),
        is_private=False,
    ).order_by("-pub_date")
    return get_polls(request, poll_list, "index.html")


def tag_cloud(request):
    return render(
        request,
        "tag_cloud.html",
        {"topTags": PollTag.topTagsPercent(15)},
    )


@login_required
def my_polls(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(), user_id=request.user
    ).order_by("-pub_date")
    return get_polls(request, poll_list, "my_polls.html")


def tagged_polls(request, tag):
    t = PollTag.objects.get(tag_text=tag.lower())
    poll_list = t.polls.all()
    return get_polls(request, poll_list, "index.html", tag=t)


@login_required
def my_info(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(), user_id=request.user
    ).order_by("-pub_date")
    paginator = Paginator(poll_list, 5)
    page = request.GET.get("page", 1)
    try:
        polls = paginator.page(page)
    except EmptyPage:
        polls = paginator.page(paginator.num_pages)
    return render(
        request,
        "my_info.html",
        {"current_user": request.user, "latest_poll_list": polls},
    )


def set_user_timezone(request):
    user_timezone = request.GET.get("timezone")
    request.session["django_timezone"] = user_timezone
    redirect_url = request.GET.get("current_path")
    return HttpResponseRedirect(redirect_url)


def get_polls(request, poll_list, render_page, tag: str = ""):
    paginator = Paginator(poll_list, 5)
    page = request.GET.get("page")
    try:
        polls = paginator.page(page)
    except PageNotAnInteger:
        polls = paginator.page(1)
    except EmptyPage:
        polls = paginator.page(paginator.num_pages)
    return render(request, render_page, {"latest_poll_list": polls, "tag": tag})


def change_suspension(request, poll_id):
    p = Poll.objects.get(id=poll_id)
    p.is_suspended = not p.is_suspended
    p.save()


def all_tags(request):
    return {"allTags": [t.tag_text for t in PollTag.objects.all()]}


class DetailView(generic.DetailView):
    model = Poll
    template_name = "detail.html"

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        poll = self.object
        user = self.request.user
        checked_choices = []
        allowed_emails = []

        # Default to setting this if the poll has been configured for it. Thus
        # the user has to opt-out of email communication if required.
        permit_email = True if poll.show_email_opt_in else False

        if poll.vtype == 1:
            context["already_voted"] = False
            # Check if cookie is already set.
            value = self.request.COOKIES.get("polls_voted")
            if value:
                try:
                    polls_voted_list = json.loads(value)
                except ValueError:
                    # Ignore if the cookie content cannot be parsed.
                    pass
                else:
                    if poll.id in polls_voted_list:
                        context["already_voted"] = True
        if poll.vtype == 2 and user.is_authenticated:
            for ballot in poll.ballot_set.all():
                if ballot.user == user:
                    for option in ballot.vote_set.all():
                        checked_choices.append(option.choice)
                    permit_email = ballot.permit_email
        elif poll.vtype == 3:
            # The user can either be authenticated, or redirected through a link.
            invitations = VoteInvitation.objects.filter(poll_id=poll.id)
            allowed_emails = []
            for invitation in invitations:
                allowed_emails.append(invitation.email)
            if user.is_authenticated and (
                user.email in allowed_emails or user == poll.user
            ):
                context["vote_authorized"] = True
                # Get the checked choices.
                for ballot in poll.ballot_set.all():
                    if ballot.user == user:
                        for option in ballot.vote_set.all():
                            checked_choices.append(option.choice)
                        permit_email = ballot.permit_email
            if "key" in self.request.GET and "email" in self.request.GET:
                invitations = VoteInvitation.objects.filter(
                    key=self.request.GET["key"],
                    email=self.request.GET["email"],
                    poll_id=poll.id,
                )
                if invitations:
                    context["vote_invitation"] = invitations[0]
                    context["vote_authorized"] = True
                    ballot = invitations[0].ballot
                    if ballot is not None:
                        for option in ballot.vote_set.all():
                            checked_choices.append(option.choice)
                        permit_email = ballot.permit_email
        context["allowed_emails"] = allowed_emails
        context["checked_choices"] = checked_choices
        context["num_tags"] = len(poll.polltag_set.all())
        context["tags"] = []
        context["permit_email"] = permit_email
        if context["num_tags"] > 0:
            context["tags"] = [t.tag_text for t in poll.polltag_set.all()]
        if not poll.is_closed() and poll.close_date is not None:
            time_diff = poll.close_date - timezone.now()
            context["time_difference"] = time_diff.total_seconds()
        return context


@login_required
def delete_poll(request, poll_id):
    logger.debug(f"Attempting to delete poll {poll_id}")
    try:
        poll = get_object_or_404(Poll, id=poll_id, user=request.user)
        logger.debug(f"Found poll: {poll}")
        poll.delete()
        messages.success(request, "Poll deleted successfully.")
        return redirect("my_polls")  # Redirect to the list of user's polls
    except Exception as e:
        logger.error(f"Error deleting poll: {str(e)}")
        return HttpResponseServerError(f"An error occurred: {str(e)}")


class ResultsView(generic.DetailView):
    model = Poll
    template_name = "results.html"

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.object

        # Approval voting logic
        choices = poll.choice_set.annotate(vote_count=Count("vote")).order_by(
            "-vote_count"
        )
        max_votes = choices.first().vote_count if choices.exists() else 0
        leading_choices = [
            choice for choice in choices if choice.vote_count == max_votes
        ]

        # Proportional voting logic
        ballots = poll.ballot_set.prefetch_related(
            Prefetch("vote_set", queryset=Vote.objects.select_related("choice"))
        )
        proportional_votes = {choice.id: 0 for choice in poll.choice_set.all()}
        total_proportional_votes = 0

        for ballot in ballots:
            approved_choices = ballot.vote_set.all().values_list("choice_id", flat=True)
            num_approved = len(approved_choices)
            if num_approved > 0:
                weight = 1 / num_approved
                for choice_id in approved_choices:
                    proportional_votes[choice_id] += weight
                    total_proportional_votes += weight

        proportional_results = [
            {
                "choice_text": choice.choice_text,
                "proportional_votes": proportional_votes[choice.id],
                "proportional_percentage": (
                    proportional_votes[choice.id] / total_proportional_votes * 100
                    if total_proportional_votes > 0
                    else 0
                ),
            }
            for choice in poll.choice_set.all()
        ]

        # Add data to context
        context.update(
            {
                "choices": choices,  # Approval results
                "leading_choices": leading_choices,
                "max_votes": max_votes,
                "proportional_results": proportional_results,  # Proportional results
                "total_proportional_votes": total_proportional_votes,
            }
        )
        return context


@require_http_methods(["POST"])
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)

    # Get the type of vote method required for this poll.
    # Type 1 - No restriction on the number of ballots.
    # Type 2 - Only users with registered accounts are allowed to vote.
    # Type 3 - Only users with the invitation email link (& poll owner) are allowed to vote.
    poll_vtype = poll.vtype

    if poll_vtype == 1:
        if not poll.is_closed():
            ballot = poll.ballot_set.create(timestamp=timezone.now())

            if "email_opt_in" and "email_address" in request.POST:
                permit_email = True
                email_address = request.POST["email_address"]
                ballot.permit_email = permit_email
                ballot.email = email_address
                ballot.save()

            for counter, choice in enumerate(poll.choice_set.all()):
                if "choice" + str(counter + 1) in request.POST:
                    ballot.vote_set.create(choice=choice)
                    ballot.save()
            for key, value in list(request.POST.items()):
                if key + "txt" in request.POST:
                    choice_txt = request.POST[key + "txt"].strip()
                    if choice_txt:
                        choice = poll.choice_set.filter(choice_text=choice_txt)
                        if not choice:
                            if "linkurl-" + key in request.POST:
                                choicelink_txt = request.POST["linkurl-" + key].strip()
                                if choicelink_txt:
                                    choice = poll.choice_set.create(
                                        choice_text=choice_txt,
                                        choice_link=choicelink_txt,
                                    )
                                else:
                                    choice = poll.choice_set.create(
                                        choice_text=choice_txt
                                    )
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
            poll.save()
            response = HttpResponseRedirect(reverse("results", args=(poll.id,)))
            value = request.COOKIES.get("polls_voted")
            if value:
                try:
                    polls_voted_list = json.loads(value)
                    polls_voted_list.append(poll.id)
                except ValueError:
                    polls_voted_list = [poll.id]
            else:
                polls_voted_list = [poll.id]

            response.set_cookie("polls_voted", json.dumps(polls_voted_list))
            return response
        else:
            return HttpResponseRedirect(reverse("detail", args=(poll.id,)))
    elif poll_vtype == 2:
        # Type 2 poll - the user is required to login to vote.
        if request.user.is_authenticated:
            # Check if a poll is closed
            if not poll.is_closed():
                # Check if a ballot exists under the users name.
                existing_ballots = Ballot.objects.filter(
                    poll_id=poll_id, user_id=request.user
                )
                if not existing_ballots:
                    # Check if email_opt_in is permitted.
                    permit_email = False
                    if "email_opt_in" in request.POST:
                        permit_email = True

                    # Add the user as the foreign key
                    ballot = poll.ballot_set.create(
                        timestamp=timezone.now(),
                        user=request.user,
                        permit_email=permit_email,
                    )

                    for counter, choice in enumerate(poll.choice_set.all()):
                        if "choice" + str(counter + 1) in request.POST:
                            ballot.vote_set.create(choice=choice)
                            ballot.save()
                    handle_write_ins(ballot, poll, request)
                    poll.save()
                    return HttpResponseRedirect(reverse("results", args=(poll.id,)))
                else:
                    ballot = poll.ballot_set.get(user=request.user)

                    # Ensure that email opt in is updated as required.
                    permit_email = False
                    if "email_opt_in" in request.POST:
                        permit_email = True

                    if ballot.permit_email != permit_email:
                        ballot.permit_email = permit_email
                        ballot.save()

                    # Ensure that votes are updated if required.
                    for counter, choice in enumerate(poll.choice_set.all()):
                        if "choice" + str(counter + 1) in request.POST:
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
                        else:
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if ballot_exist:
                                ballot_exist.delete()
                                ballot.save()
                    # Ensure that choice options are updated if required.
                    handle_write_ins(ballot, poll, request)
                    poll.save()
                    return HttpResponseRedirect(reverse("results", args=(poll.id,)))
            else:
                return HttpResponseRedirect(reverse("detail", args=(poll.id,)))
        else:
            return HttpResponseRedirect(
                reverse("account_login") + "?next=" + reverse("detail", args=(poll.id,))
            )
    elif poll_vtype == 3:
        # Type 3 - Vote through the email invitation link.
        invitations = []
        auth_user = None
        ballot = None

        # Find the appropriate ballot and user
        if "invitation_key" in request.POST and "invitation_email" in request.POST:
            invitations = VoteInvitation.objects.filter(
                key=request.POST["invitation_key"],
                email=request.POST["invitation_email"],
                poll_id=poll.id,
            )
            if invitations:
                ballot = invitations[0].ballot

            # Check for the same email for an existing user in the database.
            users = User.objects.filter(email=request.POST["invitation_email"])
            if users:
                auth_user = users[0]

        elif request.user.is_authenticated:
            auth_user = request.user
            invitations = VoteInvitation.objects.filter(
                email=request.user.email,
                poll_id=poll.id,
            )
            if invitations:
                ballot = invitations[0].ballot
            elif request.user == poll.user:
                # The owner of this poll is allowed to vote by default
                ballots = poll.ballot_set.filter(user=auth_user)
                if ballots:
                    ballot = ballots[0]

        if invitations or request.user == poll.user:
            if not poll.is_closed():
                if ballot is None:
                    # Check if email_opt_in is permitted.
                    permit_email = False
                    if "email_opt_in" in request.POST:
                        permit_email = True

                    ballot = poll.ballot_set.create(
                        timestamp=timezone.now(),
                        user=auth_user,
                        permit_email=permit_email,
                    )
                    for counter, choice in enumerate(poll.choice_set.all()):
                        if "choice" + str(counter + 1) in request.POST:
                            ballot.vote_set.create(choice=choice)
                            ballot.save()
                else:
                    # Ensure that email opt in is updated as required.
                    permit_email = False
                    if "email_opt_in" in request.POST:
                        permit_email = True

                    if ballot.permit_email != permit_email:
                        ballot.permit_email = permit_email
                        ballot.save()

                    for counter, choice in enumerate(poll.choice_set.all()):
                        if "choice" + str(counter + 1) in request.POST:
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
                        else:
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if ballot_exist:
                                ballot_exist.delete()
                                ballot.save()
                if poll.show_write_in:
                    handle_write_ins(ballot, poll, request)
                poll.save()
                if invitations:
                    invitations[0].ballot = ballot
                    invitations[0].save()
                return HttpResponseRedirect(reverse("results", args=(poll.id,)))
            else:
                return HttpResponseRedirect(reverse("detail", args=(poll.id,)))
        else:
            return HttpResponseRedirect(reverse("detail", args=(poll.id,)))


def handle_write_ins(ballot, poll, request):
    for key, value in list(request.POST.items()):
        if key + "txt" in request.POST:
            choice_txt = request.POST[key + "txt"].strip()
            if choice_txt:
                choice = poll.choice_set.filter(choice_text=choice_txt)
                if not choice:
                    if "linkurl-" + key in request.POST:
                        choicelink_txt = request.POST["linkurl-" + key].strip()
                        if choicelink_txt:
                            choice = poll.choice_set.create(
                                choice_text=choice_txt,
                                choice_link=choicelink_txt,
                            )
                        else:
                            choice = poll.choice_set.create(choice_text=choice_txt)
                    ballot_exist = ballot.vote_set.filter(choice=choice)
                    if not ballot_exist:
                        ballot.vote_set.create(choice=choice)
                        ballot.save()


def embed_instructions(request, poll_id):
    link = request.build_absolute_uri("/{}".format(poll_id))
    return render(request, "embed_instructions.html", {"link": link})


class CreateView(generic.View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, "create.html")

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        choices = []

        if "question" not in request.POST:
            return render(
                request,
                "create.html",
                {"question_error": "The question is missing"},
            )
        else:
            question = request.POST["question"].strip()

            if not question:
                return render(
                    request,
                    "create.html",
                    {"question_error": "The question is missing"},
                )

            for key in request.POST:
                # this could be done using String.startswith instead of re
                # but then it would be harder to avoid POST params
                # that aren't choices but happen to start with choice.
                # in case someone adds a "choiceType" option later.
                m = re.match(r"choice(\d+)", key)
                if m:
                    text = request.POST[key].strip()
                    if text == "":
                        continue
                    c = int(m.group(1))
                    linkname = "linkurl-choice{}".format(c)
                    if linkname in request.POST:
                        linktext = request.POST[linkname].strip()
                    else:
                        linktext = None
                    choices.append((c, text, linktext))

            choices.sort(key=lambda k: k[0])

            if not len(choices):
                return render(
                    request,
                    "create.html",
                    {
                        "choice_error": "At least one choice is required",
                        "question": question,
                    },
                )

            # The voting type to be used by the poll
            vtype = request.POST["radio-poll-type"]

            if "close-datetime" in request.POST:
                closedatetime = request.POST["close-datetime"]
            else:
                closedatetime = ""

            if closedatetime:
                closedatetime = datetime.datetime.strptime(
                    closedatetime, "%Y/%m/%d %H:%M"
                )
                current_datetime = timezone.localtime(timezone.now())
                current_tzinfo = current_datetime.tzinfo
                closedatetime = closedatetime.replace(tzinfo=current_tzinfo)
            else:
                closedatetime = None

            if "show-close-date" in request.POST:
                show_close_date = True
            else:
                show_close_date = False

            if "show-countdown" in request.POST:
                show_countdown = True
            else:
                show_countdown = False

            if "show-write-in" in request.POST:
                show_write_in = True
            else:
                show_write_in = False

            if "show-lead-color" in request.POST:
                show_lead_color = True
            else:
                show_lead_color = False

            if "show-email-opt-in" in request.POST:
                show_email_opt_in = True
            else:
                show_email_opt_in = False

            if "public-poll-visibility" in request.POST:
                is_private = False
            else:
                is_private = True

            p = Poll(
                question=question,
                pub_date=timezone.now(),
                user=request.user,
                vtype=vtype,
                close_date=closedatetime,
                show_close_date=show_close_date,
                show_countdown=show_countdown,
                show_write_in=show_write_in,
                show_lead_color=show_lead_color,
                show_email_opt_in=show_email_opt_in,
                is_private=is_private,
            )
            p.save()

            for choice in choices:
                p.choice_set.create(choice_text=choice[1], choice_link=choice[2])

            if len(str(request.POST["token-tags"])):
                p.add_tags(request.POST["token-tags"].split(","))
            if vtype == "3":
                p.send_vote_invitations(request.POST["token-emails"])

            return HttpResponseRedirect(reverse("embed_instructions", args=(p.id,)))


# class EditView(generic.View):
#     @method_decorator(login_required)
#     def get(self, request, *args, **kwargs):
#         try:
#             poll = Poll.objects.get(id=kwargs["poll_id"])
#         except Poll.DoesNotExist:
#             raise Http404("Poll does not exist")

#         if request.user != poll.user and not request.user.is_staff:
#             raise PermissionDenied

#         choices = Choice.objects.filter(poll=kwargs["poll_id"])
#         # convert closedatetime to localtime.
#         if poll.close_date:
#             closedatetime = timezone.localtime(poll.close_date)
#         return render(
#             request,
#             "edit.html",
#             {
#                 "poll": poll,
#                 "choices": choices,
#                 "closedatetime": (
#                     closedatetime.strftime("%Y/%m/%d %H:%M") if poll.close_date else ""
#                 ),
#                 "can_edit_poll": poll.can_edit(),
#                 "choices_count": Choice.objects.last().id,
#                 "blank_choices": [],
#                 "choice_blank_error": False,
#                 "existing_choice_texts": {"new": {}, "existing": {}},
#                 "existing_choice_links": {"new": {}, "existing": {}},
#                 "invited_emails": ",".join([str(r) for r in poll.invited_emails()]),
#                 "all_tags": poll.all_tags(),
#             },
#         )

#     @method_decorator(login_required)
#     def post(self, request, *args, **kwargs):
#         existing_choice_texts = {}
#         existing_choice_links = {}
#         tags_to_add = []
#         tags_to_delete = []
#         poll = Poll.objects.get(id=kwargs["poll_id"])
#         closedatetime = request.POST["close-datetime"]
#         try:
#             original_close_date = poll.close_date
#             closedatetime = datetime.datetime.strptime(closedatetime, "%Y/%m/%d %H:%M")
#             current_datetime = timezone.localtime(timezone.now())
#             current_tzinfo = current_datetime.tzinfo
#             closedatetime = closedatetime.replace(tzinfo=current_tzinfo)
#             poll.close_date = closedatetime
#         except ValueError:
#             poll.close_date = original_close_date
#         poll.show_close_date = "show-close-date" in request.POST
#         poll.show_countdown = "show-countdown" in request.POST
#         poll.is_private = "public-poll-visibility" not in request.POST
#         poll.show_write_in = "show-write-in" in request.POST
#         poll.show_lead_color = "show-lead-color" in request.POST
#         poll.show_email_opt_in = "show-email-opt-in" in request.POST
#         if "radio-poll-type" in request.POST:
#             poll.vtype = int(request.POST["radio-poll-type"])
#         poll.save()
#         if "token-emails" in request.POST:
#             poll.send_vote_invitations(request.POST["token-emails"])
#         existing_tags_set = set(poll.all_tags().split(","))
#         if len(request.POST["token-tags"]) > 0:
#             request_tags_set = set(
#                 [tag.strip() for tag in request.POST["token-tags"].split(",")]
#             )
#         else:
#             request_tags_set = set([])
#         tags_to_add = list(request_tags_set - existing_tags_set)
#         tags_to_delete = list(existing_tags_set - request_tags_set)
#         if len(tags_to_add) > 0:
#             poll.add_tags(tags_to_add)
#         if len(tags_to_delete) > 0:
#             poll.delete_tags(tags_to_delete)
#         if poll.can_edit():
#             if poll.question != request.POST["question"]:
#                 poll.question = request.POST["question"].strip()
#             choices = Choice.objects.filter(poll=kwargs["poll_id"])
#             request_choice_ids = []
#             create_data_for_text = {}
#             create_data_for_link = {}
#             update_data_for_text = {}
#             update_data_for_link = {}
#             choice_blank = False
#             for k in list(request.POST.keys()):
#                 m = re.search(r"choice(\d+)", k)
#                 if m and m.group(1):
#                     id = m.group(1)
#                     request_choice_ids.append(int(id))
#             poll_choice_ids = [choice.id for choice in choices]
#             request_choice_ids_set = set(request_choice_ids)
#             poll_choice_ids_set = set(poll_choice_ids)
#             choice_ids_for_create = request_choice_ids_set - poll_choice_ids_set
#             choice_ids_for_delete = poll_choice_ids_set - request_choice_ids_set
#             choice_ids_for_update = poll_choice_ids_set & request_choice_ids_set
#             new_choice_len = len(choice_ids_for_create)
#             update_choice_len = len(choice_ids_for_update)
#             delete_choice_len = len(choice_ids_for_delete)
#             if new_choice_len > 0:
#                 choice_ids_for_create_dup = choice_ids_for_create.copy()
#                 for i in choice_ids_for_create_dup:
#                     create_text = request.POST["choice" + (str(i))]
#                     if len(create_text) == 0:
#                         choice_ids_for_create.remove(i)
#                         continue
#                     else:
#                         create_data_for_text[i] = create_text
#                         create_data_for_link[i] = request.POST[
#                             "linkurl-choice" + (str(i))
#                         ]
#                 existing_choice_texts["new"] = create_data_for_text
#                 existing_choice_links["new"] = create_data_for_link
#             if update_choice_len > 0:
#                 blank_choices = []
#                 for i in choice_ids_for_update:
#                     update_text = request.POST["choice" + (str(i))]
#                     if len(update_text) == 0:
#                         choice_blank = True
#                         blank_choices.append(i)
#                     else:
#                         update_data_for_text[i] = update_text
#                         update_data_for_link[i] = request.POST[
#                             "linkurl-choice" + (str(i))
#                         ]
#                 existing_choice_texts["existing"] = update_data_for_text
#                 existing_choice_links["existing"] = update_data_for_link
#             # If any current poll choices are left blank by user
#             if choice_blank:
#                 ccount = Choice.objects.last().id + new_choice_len
#                 return render(
#                     request,
#                     "edit.html",
#                     {
#                         "poll": poll,
#                         "choices": choices,
#                         "choice_blank_error": choice_blank,
#                         "choices_count": ccount,
#                         "can_edit_poll": poll.can_edit(),
#                         "blank_choices": blank_choices,
#                         "existing_choice_texts": existing_choice_texts,
#                         "existing_choice_links": existing_choice_links,
#                         "invited_emails": ",".join(
#                             [str(r) for r in poll.invited_emails()]
#                         ),
#                         "all_tags": poll.all_tags(),
#                     },
#                 )

#             # No current poll choices are blank, so go ahead and update, create, delete choices
#             if new_choice_len > 0:
#                 poll.add_choices(
#                     choice_ids_for_create, create_data_for_text, create_data_for_link
#                 )
#             if update_choice_len > 0:
#                 poll.update_choices(
#                     choice_ids_for_update, update_data_for_text, update_data_for_link
#                 )
#             if delete_choice_len > 0:
#                 poll.delete_choices(choice_ids_for_delete)

#             poll.save()

#         return HttpResponseRedirect(reverse("my_polls"))


def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/")


def loginView(request):
    context = {}
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return HttpResponseRedirect("/")
        context["invalid"] = True
    return render(request, "registration/login.html", context)

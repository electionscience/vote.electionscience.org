import datetime
import json
import re

import structlog
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Prefetch
from django.http import HttpResponseRedirect, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_http_methods

from approval_polls.models import Poll, PollTag, Vote, VoteInvitation

logger = structlog.get_logger(__name__)


def index(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(),
        is_private=False,
    ).order_by("-pub_date")[:100]
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
    t = get_object_or_404(PollTag, tag_text=tag.lower())
    poll_list = t.polls.all()
    return get_polls(request, poll_list, "index.html", tag=t.tag_text)


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

        proportional_results = sorted(
            [
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
            ],
            key=lambda x: x[
                "proportional_percentage"
            ],  # Sort by proportional_percentage
            reverse=True,  # Highest percentage first
        )

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


def raw_ballots(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id, pub_date__lte=timezone.now())
    # Check if the poll is private
    if poll.is_private:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if request.user != poll.user:
            return JsonResponse({"error": "Access denied"}, status=403)
    # Check for polls with invitation-only access (vtype=3)
    if poll.vtype == 3:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if request.user != poll.user:
            invitations = VoteInvitation.objects.filter(
                email=request.user.email, poll_id=poll.id
            )

            if not invitations:
                return JsonResponse({"error": "Access denied"}, status=403)

    ballots = poll.ballot_set.prefetch_related("vote_set")
    raw_ballots_data = []
    for ballot in ballots:
        approved_choice_ids = list(ballot.vote_set.values_list("choice_id", flat=True))
        raw_ballots_data.append(approved_choice_ids)

    # We must also return choices if we're trying to consume them in JS
    # 'choice_text' is used for the Chart.js labels, so send them along:
    choices_data = list(poll.choice_set.values("id", "choice_text"))

    return JsonResponse(
        {
            "ballots": raw_ballots_data,
            "choices": choices_data,  # <--- Make sure we're returning this!
        }
    )


def create_ballot(poll, user=None, permit_email=False):
    return poll.ballot_set.create(
        timestamp=timezone.now(), user=user, permit_email=permit_email
    )


def update_ballot_votes(ballot, poll, request):
    for counter, choice in enumerate(poll.choice_set.all()):
        choice_key = f"choice{counter + 1}"
        if choice_key in request.POST:
            if not ballot.vote_set.filter(choice=choice).exists():
                ballot.vote_set.create(choice=choice)
        else:
            ballot.vote_set.filter(choice=choice).delete()
    handle_write_ins(ballot, poll, request)


def handle_email_opt_in(request):
    return "email_opt_in" in request.POST


@require_http_methods(["POST"])
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if poll.is_closed():
        return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

    poll_vtype = poll.vtype
    user = request.user if request.user.is_authenticated else None
    ballot = None

    if poll_vtype == 1:
        ballot = create_ballot(poll, permit_email=handle_email_opt_in(request))
    elif poll_vtype == 2 and user:
        ballot, created = poll.ballot_set.get_or_create(
            user=user, defaults={"permit_email": handle_email_opt_in(request)}
        )
    elif poll_vtype == 3:
        invitation_key = request.POST.get("invitation_key")
        invitation_email = request.POST.get("invitation_email")
        invitations = VoteInvitation.objects.filter(
            key=invitation_key, email=invitation_email, poll_id=poll.id
        )
        if invitations.exists():
            ballot = invitations.first().ballot
        elif user:
            ballot, created = poll.ballot_set.get_or_create(
                user=user, defaults={"permit_email": handle_email_opt_in(request)}
            )

    if ballot:
        update_ballot_votes(ballot, poll, request)
        poll.save()
        return HttpResponseRedirect(reverse("results", args=(poll.id,)))

    return HttpResponseRedirect(
        reverse("account_login") + "?next=" + reverse("detail", args=(poll.id,))
    )


def handle_write_ins(ballot, poll, request):
    for key, value in request.POST.items():
        choice_txt = request.POST.get(f"{key}txt", "").strip()
        if not choice_txt:
            continue

        choice, created = poll.choice_set.get_or_create(
            choice_text=choice_txt, defaults={}
        )

        if created:
            choicelink_txt = request.POST.get(f"linkurl-{key}", "").strip()
            if choicelink_txt:
                choice.choice_link = choicelink_txt
                choice.save()

        if not ballot.vote_set.filter(choice=choice).exists():
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

            if "token-tags" in request.POST and len(str(request.POST["token-tags"])):
                p.add_tags(request.POST["token-tags"].split(","))
            if vtype == "3":
                p.send_vote_invitations(request.POST["token-emails"])

            return HttpResponseRedirect(reverse("embed_instructions", args=(p.id,)))

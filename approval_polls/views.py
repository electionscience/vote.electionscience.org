import datetime
import json
import re
from collections import Counter, defaultdict

import structlog
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Count, Prefetch
from django.http import HttpResponseRedirect, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_http_methods

from approval_polls.models import Ballot, Poll, PollTag, Vote, VoteInvitation

logger = structlog.get_logger(__name__)


def index(request):
    if request.user.is_authenticated:
        poll_list = (
            Poll.objects.filter(
                user=request.user,
            )
            .select_related("user")
            .prefetch_related("choice_set", "polltag_set", "ballot_set")
            .order_by("-pub_date")
        )
    else:
        poll_list = Poll.objects.none()
    return get_polls(request, poll_list, "index.html")


def tag_cloud(request):
    return render(
        request,
        "tag_cloud.html",
        {"topTags": PollTag.topTagsPercent(15)},
    )


@login_required
def my_polls(request):
    # Handle POST requests for toggling settings
    if request.method == "POST":
        poll_id = request.POST.get("poll_id")
        if poll_id:
            poll = get_object_or_404(Poll, id=poll_id, user=request.user)
            if "toggle_suspended" in request.POST:
                poll.is_suspended = not poll.is_suspended
                poll.save()
                status = "closed" if poll.is_suspended else "opened"
                messages.success(request, f"Poll has been {status}.")
            elif "toggle_visibility" in request.POST:
                poll.is_private = not poll.is_private
                poll.save()
                visibility = "private" if poll.is_private else "public"
                messages.success(request, f"Poll visibility set to {visibility}.")
            return redirect("my_polls")

    poll_list = (
        Poll.objects.filter(pub_date__lte=timezone.now(), user_id=request.user)
        .select_related("user")
        .prefetch_related("choice_set", "polltag_set", "ballot_set__user")
        .order_by("-pub_date")
    )

    # Prepare voter information for each poll
    polls_with_voters = []
    for poll in poll_list:
        ballots = poll.ballot_set.select_related("user").order_by("-timestamp")
        voters = []
        if poll.vtype == 1:
            # Anonymous polls: show only timestamp
            for ballot in ballots:
                voters.append(
                    {
                        "timestamp": ballot.timestamp,
                        "username": None,
                        "email": None,
                    }
                )
        else:
            # Authenticated polls: show username, email (if available), and timestamp
            for ballot in ballots:
                username = ballot.user.username if ballot.user else None
                email = (
                    ballot.email
                    if ballot.email
                    else (ballot.user.email if ballot.user else None)
                )
                voters.append(
                    {
                        "timestamp": ballot.timestamp,
                        "username": username,
                        "email": email,
                    }
                )

        polls_with_voters.append(
            {
                "poll": poll,
                "voters": voters,
                "total_voters": len(voters),
            }
        )

    paginator = Paginator(polls_with_voters, 5)
    page = request.GET.get("page")
    try:
        polls = paginator.page(page)
    except PageNotAnInteger:
        polls = paginator.page(1)
    except EmptyPage:
        polls = paginator.page(paginator.num_pages)

    return render(request, "my_polls.html", {"latest_poll_list": polls})


def tagged_polls(request, tag):
    t = get_object_or_404(PollTag, tag_text=tag.lower())
    poll_list = (
        t.polls.filter(pub_date__lte=timezone.now(), is_private=False)
        .select_related("user")
        .prefetch_related("choice_set", "polltag_set")
        .order_by("-pub_date")
    )
    return get_polls(request, poll_list, "index.html", tag=t.tag_text)


@login_required
def my_info(request):
    # Handle POST requests for toggling settings
    if request.method == "POST":
        poll_id = request.POST.get("poll_id")
        if poll_id:
            poll = get_object_or_404(Poll, id=poll_id, user=request.user)
            if "toggle_suspended" in request.POST:
                poll.is_suspended = not poll.is_suspended
                poll.save()
                status = "closed" if poll.is_suspended else "opened"
                messages.success(request, f"Poll has been {status}.")
            elif "toggle_visibility" in request.POST:
                poll.is_private = not poll.is_private
                poll.save()
                visibility = "private" if poll.is_private else "public"
                messages.success(request, f"Poll visibility set to {visibility}.")
            return redirect("my_info")

    poll_list = (
        Poll.objects.filter(pub_date__lte=timezone.now(), user_id=request.user)
        .select_related("user")
        .prefetch_related("ballot_set__user")
        .order_by("-pub_date")
    )

    # Prepare voter information for each poll
    polls_with_voters = []
    for poll in poll_list:
        ballots = poll.ballot_set.select_related("user").order_by("-timestamp")
        voters = []
        if poll.vtype == 1:
            # Anonymous polls: show only timestamp
            for ballot in ballots:
                voters.append(
                    {
                        "timestamp": ballot.timestamp,
                        "username": None,
                        "email": None,
                    }
                )
        else:
            # Authenticated polls: show username, email (if available), and timestamp
            for ballot in ballots:
                username = ballot.user.username if ballot.user else None
                email = (
                    ballot.email
                    if ballot.email
                    else (ballot.user.email if ballot.user else None)
                )
                voters.append(
                    {
                        "timestamp": ballot.timestamp,
                        "username": username,
                        "email": email,
                    }
                )

        polls_with_voters.append(
            {
                "poll": poll,
                "voters": voters,
                "total_voters": len(voters),
            }
        )

    paginator = Paginator(polls_with_voters, 5)
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


@login_required
def poll_admin(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    # Verify user is the poll creator
    if poll.user != request.user:
        messages.error(request, "You are not authorized to access this page.")
        return redirect("detail", pk=poll_id)

    # Handle POST requests for toggling settings
    if request.method == "POST":
        if "toggle_suspended" in request.POST:
            poll.is_suspended = not poll.is_suspended
            poll.save()
            status = "closed" if poll.is_suspended else "opened"
            messages.success(request, f"Poll has been {status}.")
        elif "toggle_visibility" in request.POST:
            poll.is_private = not poll.is_private
            poll.save()
            visibility = "private" if poll.is_private else "public"
            messages.success(request, f"Poll visibility set to {visibility}.")
        return redirect("detail", pk=poll_id)

    # Get ballots with related user data
    ballots = poll.ballot_set.select_related("user").order_by("-timestamp")

    # Prepare voter information based on poll type
    voters = []
    if poll.vtype == 1:
        # Anonymous polls: show only timestamp
        for ballot in ballots:
            voters.append(
                {
                    "timestamp": ballot.timestamp,
                    "username": None,
                    "email": None,
                }
            )
    else:
        # Authenticated polls: show username, email (if available), and timestamp
        for ballot in ballots:
            username = ballot.user.username if ballot.user else None
            email = (
                ballot.email
                if ballot.email
                else (ballot.user.email if ballot.user else None)
            )
            voters.append(
                {
                    "timestamp": ballot.timestamp,
                    "username": username,
                    "email": email,
                }
            )

    context = {
        "poll": poll,
        "voters": voters,
        "total_voters": len(voters),
    }

    return render(request, "poll_admin.html", context)


def all_tags(request):
    return {"allTags": [t.tag_text for t in PollTag.objects.all()]}


class DetailView(generic.DetailView):
    model = Poll
    template_name = "detail.html"

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now()).prefetch_related(
            Prefetch(
                "ballot_set",
                queryset=Ballot.objects.prefetch_related(
                    Prefetch("vote_set", queryset=Vote.objects.select_related("choice"))
                ),
            )
        )

    def get(self, request, *args, **kwargs):
        # Check if poll is private and user is not authenticated
        self.object = self.get_object()
        if self.object.is_private and not request.user.is_authenticated:
            messages.error(request, "This poll is private. Please log in to access it.")
            return redirect("account_login")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        poll = self.object
        user = self.request.user
        checked_choices = []
        allowed_emails = []

        # Default to setting this if the poll has been configured for it. Thus
        # the user has to opt-out of email communication if required.
        permit_email = True if poll.show_email_opt_in else False

        # Add admin data if user is the poll creator
        if user.is_authenticated and poll.user == user:
            ballots = poll.ballot_set.select_related("user").order_by("-timestamp")
            voters = []
            if poll.vtype == 1:
                # Anonymous polls: show only timestamp
                for ballot in ballots:
                    voters.append(
                        {
                            "timestamp": ballot.timestamp,
                            "username": None,
                            "email": None,
                        }
                    )
            else:
                # Authenticated polls: show username, email (if available), and timestamp
                for ballot in ballots:
                    username = ballot.user.username if ballot.user else None
                    email = (
                        ballot.email
                        if ballot.email
                        else (ballot.user.email if ballot.user else None)
                    )
                    voters.append(
                        {
                            "timestamp": ballot.timestamp,
                            "username": username,
                            "email": email,
                        }
                    )
            context["voters"] = voters
            context["total_voters"] = len(voters)

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
        with transaction.atomic():
            poll = get_object_or_404(Poll, id=poll_id, user=request.user)
            logger.debug(f"Found poll: {poll}")

            # Delete related objects first to avoid potential cascade issues
            poll.choice_set.all().delete()
            poll.ballot_set.all().delete()
            poll.voteinvitation_set.all().delete()
            poll.polltag_set.clear()  # Remove tag associations without deleting tags

            poll.delete()
            messages.success(request, "Poll deleted successfully.")

        return redirect("my_polls")  # Redirect to the list of user's polls
    except Poll.DoesNotExist:
        logger.warning(f"Poll {poll_id} not found or user not authorized")
        messages.error(
            request, "Poll not found or you are not authorized to delete it."
        )
        return redirect("my_polls")
    except Exception as e:
        logger.error(f"Error deleting poll: {str(e)}")
        messages.error(request, "An error occurred while deleting the poll.")
        return HttpResponseServerError(f"An error occurred: {str(e)}")


class ResultsView(generic.DetailView):
    model = Poll
    template_name = "results.html"

    def get(self, request, *args, **kwargs):
        # Check if poll is private and user is not authenticated
        self.object = self.get_object()
        if self.object.is_private and not request.user.is_authenticated:
            messages.error(request, "This poll is private. Please log in to access it.")
            return redirect("account_login")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

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

        # Cast vote record analysis
        total_ballots = poll.total_ballots()
        num_choices = poll.choice_set.count()
        co_approvals = []
        approval_distribution = Counter()
        candidate_approval_distributions = defaultdict(Counter)
        anyone_but_analysis = Counter()

        # Only calculate if we have enough data
        if total_ballots >= 2 and num_choices >= 2:
            # Build ballot approvals mapping
            ballot_approvals = {}
            for ballot in ballots:
                approved_choice_ids = set(
                    ballot.vote_set.all().values_list("choice_id", flat=True)
                )
                ballot_approvals[ballot.id] = approved_choice_ids
                num_approved = len(approved_choice_ids)
                approval_distribution[num_approved] += 1

                # Per-candidate approval distributions
                for choice_id in approved_choice_ids:
                    candidate_approval_distributions[choice_id][num_approved] += 1

            # Calculate co-approval matrix
            choice_list = list(poll.choice_set.all())
            for i, choice_a in enumerate(choice_list):
                # Get ballots that approved choice_a
                choice_a_ballots = [
                    ballot_id
                    for ballot_id, approved in ballot_approvals.items()
                    if choice_a.id in approved
                ]
                choice_a_count = len(choice_a_ballots)

                if choice_a_count == 0:
                    continue

                for j, choice_b in enumerate(choice_list):
                    if i == j:
                        continue

                    # Count how many of choice_a's ballots also approved choice_b
                    both_count = sum(
                        1
                        for ballot_id in choice_a_ballots
                        if choice_b.id in ballot_approvals[ballot_id]
                    )

                    co_approval_rate = (both_count / choice_a_count) * 100

                    co_approvals.append(
                        {
                            "candidateA": choice_a.choice_text,
                            "candidateB": choice_b.choice_text,
                            "coApprovalCount": both_count,
                            "coApprovalRate": co_approval_rate,
                        }
                    )

            # Calculate "Anyone But" analysis - ballots with exactly N-1 approvals
            all_choice_ids = set(choice.id for choice in choice_list)
            for ballot_id, approved_choice_ids in ballot_approvals.items():
                if len(approved_choice_ids) == num_choices - 1:
                    # Find the excluded choice
                    excluded_choice_ids = all_choice_ids - approved_choice_ids
                    if len(excluded_choice_ids) == 1:
                        excluded_choice_id = list(excluded_choice_ids)[0]
                        excluded_choice = next(
                            c for c in choice_list if c.id == excluded_choice_id
                        )
                        anyone_but_analysis[excluded_choice.choice_text] += 1

        # Convert Counter objects to regular dicts for template
        approval_distribution_dict = dict(approval_distribution)
        candidate_approval_distributions_dict = {
            choice.choice_text: dict(candidate_approval_distributions[choice.id])
            for choice in poll.choice_set.all()
            if choice.id in candidate_approval_distributions
        }
        anyone_but_analysis_dict = dict(anyone_but_analysis)

        # Sort choices by vote count for consistent ordering
        # Use the annotated choices queryset which already has vote_count
        sorted_choices = list(choices)
        choices_list = [choice.choice_text for choice in sorted_choices]

        # Pre-process approval distribution matrix data
        max_approvals = (
            max(approval_distribution_dict.keys()) if approval_distribution_dict else 0
        )
        approval_distribution_matrix = []

        # Overall row
        if approval_distribution_dict:
            overall_row = {
                "name": "All Candidates",
                "is_overall": True,
                "total_voters": total_ballots,
                "distributions": [],
            }
            for num_approvals in range(1, max_approvals + 1):
                count = approval_distribution_dict.get(num_approvals, 0)
                percentage = (count / total_ballots * 100) if total_ballots > 0 else 0
                overall_row["distributions"].append(
                    {
                        "num_approvals": num_approvals,
                        "count": count,
                        "percentage": percentage,
                    }
                )
            approval_distribution_matrix.append(overall_row)

        # Per-candidate rows
        for choice in sorted_choices:
            choice_name = choice.choice_text
            if choice_name in candidate_approval_distributions_dict:
                candidate_dist = candidate_approval_distributions_dict[choice_name]
                total_voters = sum(candidate_dist.values())
                candidate_row = {
                    "name": choice_name,
                    "is_overall": False,
                    "total_voters": total_voters,
                    "distributions": [],
                }
                for num_approvals in range(1, max_approvals + 1):
                    count = candidate_dist.get(num_approvals, 0)
                    percentage = (count / total_voters * 100) if total_voters > 0 else 0
                    candidate_row["distributions"].append(
                        {
                            "num_approvals": num_approvals,
                            "count": count,
                            "percentage": percentage,
                        }
                    )
                approval_distribution_matrix.append(candidate_row)

        # Pre-process co-approval matrix data (nested dict for easier template access)
        co_approval_matrix = {}
        max_co_approval_rate = 0
        for co_approval in co_approvals:
            candidate_a = co_approval["candidateA"]
            candidate_b = co_approval["candidateB"]
            if candidate_a not in co_approval_matrix:
                co_approval_matrix[candidate_a] = {}
            co_approval_matrix[candidate_a][candidate_b] = co_approval
            if co_approval["coApprovalRate"] > max_co_approval_rate:
                max_co_approval_rate = co_approval["coApprovalRate"]
        # Ensure max is at least 1 to avoid division by zero in CSS
        if max_co_approval_rate == 0:
            max_co_approval_rate = 1

        # Pre-process anyone but analysis (sorted by count descending)
        anyone_but_sorted = sorted(
            anyone_but_analysis_dict.items(), key=lambda x: x[1], reverse=True
        )
        total_exclusions = sum(anyone_but_analysis_dict.values())

        voting_patterns = {
            "totalBallots": total_ballots,
            "approvalDistribution": approval_distribution_dict,
            "candidateApprovalDistributions": candidate_approval_distributions_dict,
            "anyoneButAnalysis": anyone_but_analysis_dict,
        }

        # Add data to context
        context.update(
            {
                "choices": choices,  # Approval results
                "leading_choices": leading_choices,
                "max_votes": max_votes,
                "proportional_results": proportional_results,  # Proportional results
                "total_proportional_votes": total_proportional_votes,
                "co_approvals": co_approvals,  # Cast vote record analysis
                "voting_patterns": voting_patterns,
                "choices_list": choices_list,
                "approval_distribution_matrix": approval_distribution_matrix,
                "max_approvals": max_approvals,
                "co_approval_matrix": co_approval_matrix,
                "max_co_approval_rate": (
                    max_co_approval_rate if max_co_approval_rate > 0 else 1
                ),
                "anyone_but_sorted": anyone_but_sorted,
                "total_exclusions": total_exclusions,
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

    ballots = poll.ballot_set.prefetch_related(
        Prefetch("vote_set", queryset=Vote.objects.select_related("choice"))
    )
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
    try:
        with transaction.atomic():
            poll = get_object_or_404(Poll, pk=poll_id)

            # Check if poll is closed
            if poll.is_closed():
                messages.error(request, "This poll is closed.")
                return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

            # Check if poll is suspended
            if poll.is_suspended:
                messages.error(request, "This poll is currently suspended.")
                return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

            poll_vtype = poll.vtype
            user = request.user if request.user.is_authenticated else None
            ballot = None

            # Handle different voting types
            if poll_vtype == 1:
                ballot = create_ballot(poll, permit_email=handle_email_opt_in(request))
            elif poll_vtype == 2:
                if not user:
                    messages.error(
                        request, "You must be logged in to vote in this poll."
                    )
                    return HttpResponseRedirect(
                        reverse("account_login")
                        + "?next="
                        + reverse("detail", args=(poll.id,))
                    )
                ballot, created = poll.ballot_set.get_or_create(
                    user=user, defaults={"permit_email": handle_email_opt_in(request)}
                )
                if not created:
                    messages.warning(
                        request,
                        "You have already voted in this poll. Your vote will be updated.",
                    )
            elif poll_vtype == 3:
                invitation_key = request.POST.get("invitation_key")
                invitation_email = request.POST.get("invitation_email")

                if not invitation_key or not invitation_email:
                    messages.error(request, "Invalid invitation details provided.")
                    return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

                invitations = VoteInvitation.objects.filter(
                    key=invitation_key, email=invitation_email, poll_id=poll.id
                )
                if invitations.exists():
                    ballot = invitations.first().ballot
                elif user:
                    if user.email not in poll.invited_emails():
                        messages.error(
                            request, "You are not invited to vote in this poll."
                        )
                        return HttpResponseRedirect(reverse("detail", args=(poll.id,)))
                    ballot, created = poll.ballot_set.get_or_create(
                        user=user,
                        defaults={"permit_email": handle_email_opt_in(request)},
                    )

            if ballot:
                update_ballot_votes(ballot, poll, request)
                messages.success(request, "Your vote has been recorded successfully.")
                return HttpResponseRedirect(reverse("results", args=(poll.id,)))
            else:
                messages.error(request, "Unable to record your vote. Please try again.")
                return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

    except Exception as e:
        logger.error(f"Error processing vote: {str(e)}")
        messages.error(request, "An error occurred while processing your vote.")
        return HttpResponseRedirect(reverse("detail", args=(poll.id,)))

    return HttpResponseRedirect(
        reverse("account_login") + "?next=" + reverse("detail", args=(poll.id,))
    )


def handle_write_ins(ballot, poll, request):
    with transaction.atomic():
        for key, value in request.POST.items():
            choice_txt = request.POST.get(f"{key}txt", "").strip()
            if not choice_txt:
                continue

            # Validate write-in text length
            if len(choice_txt) > 200:  # Match model's max_length
                logger.warning(f"Write-in text too long: {choice_txt[:50]}...")
                continue

            try:
                # Use select_for_update to prevent race conditions
                choice = (
                    poll.choice_set.select_for_update()
                    .filter(choice_text=choice_txt)
                    .first()
                )

                if not choice:
                    choice = poll.choice_set.create(
                        choice_text=choice_txt,
                        choice_link=request.POST.get(f"linkurl-{key}", "").strip(),
                    )

                # Create vote if it doesn't exist
                if not ballot.vote_set.filter(choice=choice).exists():
                    ballot.vote_set.create(choice=choice)

            except Exception as e:
                logger.error(f"Error processing write-in vote: {str(e)}")
                continue


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

            # Bulk create choices
            choice_objects = [
                Poll.choice_set.field.model(
                    poll=p, choice_text=choice[1], choice_link=choice[2]
                )
                for choice in choices
            ]
            Poll.choice_set.field.model.objects.bulk_create(choice_objects)

            if "token-tags" in request.POST and len(str(request.POST["token-tags"])):
                p.add_tags(request.POST["token-tags"].split(","))
            if vtype == "3":
                p.send_vote_invitations(request.POST["token-emails"])

            return HttpResponseRedirect(reverse("detail", args=(p.id,)))

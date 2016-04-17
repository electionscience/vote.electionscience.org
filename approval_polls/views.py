import datetime
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.http import require_http_methods

from approval_polls.models import Ballot, Poll, VoteInvitation


def index(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(),
        is_private=False,
    ).order_by('-pub_date')
    return getPolls(request, poll_list, 'approval_polls/index.html')


@login_required
def myPolls(request):
    poll_list = Poll.objects.filter(
        pub_date__lte=timezone.now(),
        user_id=request.user
    ).order_by('-pub_date')
    return getPolls(request, poll_list, 'approval_polls/my_polls.html')


@login_required
def myInfo(request):
    return render(
        request,
        'approval_polls/my_info.html',
        {'current_user': request.user}
    )


def set_user_timezone(request):
    user_timezone = request.GET.get('timezone')
    request.session['django_timezone'] = user_timezone
    redirect_url = request.GET.get('current_path')
    return HttpResponseRedirect(redirect_url)


def getPolls(request, poll_list, render_page):
    paginator = Paginator(poll_list, 5)
    page = request.GET.get('page')
    try:
        polls = paginator.page(page)
    except PageNotAnInteger:
        polls = paginator.page(1)
    except EmptyPage:
        polls = paginator.page(paginator.num_pages)
    return render(request, render_page, {'latest_poll_list': polls})


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'approval_polls/detail.html'

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        poll = self.object
        user = self.request.user
        checked_choices = []
        allowed_emails = []
        if poll.vtype == 2 and user.is_authenticated():
            for ballot in poll.ballot_set.all():
                if ballot.user == user:
                    for option in ballot.vote_set.all():
                        checked_choices.append(option.choice)
        elif poll.vtype == 3:
            # The user can either be authenticated, or redirected through a link.
            invitations = VoteInvitation.objects.filter(poll_id=poll.id)
            allowed_emails = []
            for invitation in invitations:
                allowed_emails.append(invitation.email)
            if user.is_authenticated():
                # If the user is authenticated, the poll should be accessible from the home
                # page, if it is public.
                if user.email in allowed_emails or user == poll.user:
                    context['vote_authorized'] = True
                    # Get the checked choices.
                    for ballot in poll.ballot_set.all():
                        if ballot.user == user:
                            for option in ballot.vote_set.all():
                                checked_choices.append(option.choice)
            if 'key' in self.request.GET and 'email' in self.request.GET:
                invitations = VoteInvitation.objects.filter(
                    key=self.request.GET['key'],
                    email=self.request.GET['email'],
                    poll_id=poll.id,
                )
                if invitations:
                    context['vote_invitation'] = invitations[0]
                    context['vote_authorized'] = True
                    ballot = invitations[0].ballot
                    if ballot is not None:
                        for option in ballot.vote_set.all():
                            checked_choices.append(option.choice)
        context['allowed_emails'] = allowed_emails
        context['checked_choices'] = checked_choices
        if not poll.is_closed() and poll.close_date is not None:
            time_diff = poll.close_date - timezone.now()
            context['time_difference'] = time_diff.total_seconds()
        return context

    def delete(self, request, *args, **kwargs):
        poll_id = self.get_object().id
        Poll.objects.filter(id=poll_id).delete()
        return HttpResponseRedirect('/approval_polls/my-polls/')


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'approval_polls/results.html'

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        poll = self.object
        choices = {}
        for choice in poll.choice_set.all():
            choices[choice] = choice.votes()
        maxvotes = max(choices.values())
        if maxvotes == 0:
            leading_choices = []
        else:
            leading_choices = [k for k, v in choices.items() if v == maxvotes]
        context['leading_choices'] = leading_choices
        return context


@require_http_methods(['POST'])
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
            for counter, choice in enumerate(poll.choice_set.all()):
                if 'choice' + str(counter + 1) in request.POST:
                    ballot.vote_set.create(choice=choice)
                    ballot.save()
            for key, value in request.POST.items():
                if key + 'txt' in request.POST:
                    choice_txt = request.POST[key + 'txt'].strip()
                    if choice_txt:
                        choice = poll.choice_set.filter(choice_text=choice_txt)
                        if not choice:
                            if 'linkurl-' + key in request.POST:
                                choicelink_txt = request.POST['linkurl-' + key].strip()
                            if choicelink_txt:
                                choice = poll.choice_set.create(
                                    choice_text=choice_txt,
                                    choice_link=choicelink_txt
                                    )
                            else:
                                choice = poll.choice_set.create(choice_text=choice_txt)
                            ballot_exist = ballot.vote_set.filter(choice=choice)
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
            poll.save()
            return HttpResponseRedirect(
                reverse('approval_polls:results', args=(poll.id,))
            )
        else:
            return HttpResponseRedirect(
                reverse('approval_polls:detail', args=(poll.id,))
                )
    elif poll_vtype == 2:
        # Type 2 poll - the user is required to login to vote.
        if request.user.is_authenticated():
            # Check if a poll is closed
            if not poll.is_closed():
                # Check if a ballot exists under the users name.
                existing_ballots = Ballot.objects.filter(
                    poll_id=poll_id,
                    user_id=request.user
                )
                if not existing_ballots:
                    # Add the user as the foreign key
                    ballot = poll.ballot_set.create(
                        timestamp=timezone.now(),
                        user=request.user
                    )

                    for counter, choice in enumerate(poll.choice_set.all()):
                        if 'choice' + str(counter + 1) in request.POST:
                            ballot.vote_set.create(choice=choice)
                            ballot.save()
                    for key, value in request.POST.items():
                        if key + 'txt' in request.POST:
                            choice_txt = request.POST[key + 'txt'].strip()
                            if choice_txt:
                                choice = poll.choice_set.filter(choice_text=choice_txt)
                                if not choice:
                                    if 'linkurl-' + key in request.POST:
                                        choicelink_txt = request.POST['linkurl-' + key].strip()
                                    if choicelink_txt:
                                        choice = poll.choice_set.create(
                                            choice_text=choice_txt,
                                            choice_link=choicelink_txt
                                            )
                                    else:
                                        choice = poll.choice_set.create(choice_text=choice_txt)
                                    ballot_exist = ballot.vote_set.filter(choice=choice)
                                    if not ballot_exist:
                                        ballot.vote_set.create(choice=choice)
                                        ballot.save()
                    poll.save()
                    return HttpResponseRedirect(
                        reverse('approval_polls:results', args=(poll.id,))
                    )
                else:
                    ballot = poll.ballot_set.get(user=request.user)
                    for counter, choice in enumerate(poll.choice_set.all()):
                        if 'choice' + str(counter + 1) in request.POST:
                            ballot_exist = ballot.vote_set.filter(
                                choice=choice
                                )
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
                        else:
                            ballot_exist = ballot.vote_set.filter(
                                choice=choice
                                )
                            if ballot_exist:
                                ballot_exist.delete()
                                ballot.save()
                    for key, value in request.POST.items():
                        if key + 'txt' in request.POST:
                            choice_txt = request.POST[key + 'txt'].strip()
                            if choice_txt:
                                choice = poll.choice_set.filter(choice_text=choice_txt)
                                if not choice:
                                    if 'linkurl-' + key in request.POST:
                                        choicelink_txt = request.POST['linkurl-' + key].strip()
                                    if choicelink_txt:
                                        choice = poll.choice_set.create(
                                            choice_text=choice_txt,
                                            choice_link=choicelink_txt
                                            )
                                    else:
                                        choice = poll.choice_set.create(choice_text=choice_txt)
                                    ballot_exist = ballot.vote_set.filter(choice=choice)
                                    if not ballot_exist:
                                        ballot.vote_set.create(choice=choice)
                                        ballot.save()
                    poll.save()
                    return HttpResponseRedirect(
                        reverse('approval_polls:results', args=(poll.id,))
                        )
            else:
                return HttpResponseRedirect(
                    reverse('approval_polls:detail', args=(poll.id,))
                    )
        else:
            return HttpResponseRedirect(
                reverse('auth_login') + '?next=' +
                reverse('approval_polls:detail', args=(poll.id,))
            )
    elif poll_vtype == 3:
        # Type 3 - Vote through the email invitation link.
        invitations = []
        auth_user = None
        ballot = None

        # Find the appropriate ballot and user
        if 'invitation_key' in request.POST and 'invitation_email' in request.POST:
            invitations = VoteInvitation.objects.filter(
                key=request.POST['invitation_key'],
                email=request.POST['invitation_email'],
                poll_id=poll.id,
            )
            if invitations:
                ballot = invitations[0].ballot

            # Check for the same email for an existing user in the database.
            users = User.objects.filter(email=request.POST['invitation_email'])
            if users:
                auth_user = users[0]

        elif request.user.is_authenticated():
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
                    ballot = poll.ballot_set.create(timestamp=timezone.now(), user=auth_user)
                    for counter, choice in enumerate(poll.choice_set.all()):
                        if 'choice' + str(counter + 1) in request.POST:
                            ballot.vote_set.create(choice=choice)
                            ballot.save()
                else:
                    for counter, choice in enumerate(poll.choice_set.all()):
                        if 'choice' + str(counter + 1) in request.POST:
                            ballot_exist = ballot.vote_set.filter(
                                choice=choice
                            )
                            if not ballot_exist:
                                ballot.vote_set.create(choice=choice)
                                ballot.save()
                        else:
                            ballot_exist = ballot.vote_set.filter(
                                choice=choice
                            )
                            if ballot_exist:
                                ballot_exist.delete()
                                ballot.save()
                if poll.show_write_in:
                    for key, value in request.POST.items():
                        if key + 'txt' in request.POST:
                            choice_txt = request.POST[key + 'txt'].strip()
                            if choice_txt:
                                choice = poll.choice_set.filter(choice_text=choice_txt)
                                if not choice:
                                    if 'linkurl-' + key in request.POST:
                                        choicelink_txt = request.POST['linkurl-' + key].strip()
                                    if choicelink_txt:
                                        choice = poll.choice_set.create(
                                            choice_text=choice_txt,
                                            choice_link=choicelink_txt
                                            )
                                    else:
                                        choice = poll.choice_set.create(choice_text=choice_txt)
                                    ballot_exist = ballot.vote_set.filter(choice=choice)
                                    if not ballot_exist:
                                        ballot.vote_set.create(choice=choice)
                                        ballot.save()
                poll.save()
                if invitations:
                    invitations[0].ballot = ballot
                    invitations[0].save()
                return HttpResponseRedirect(
                    reverse('approval_polls:results', args=(poll.id,))
                )
            else:
                return HttpResponseRedirect(
                    reverse('approval_polls:detail', args=(poll.id,))
                )
        else:
            return HttpResponseRedirect(
                reverse('approval_polls:detail', args=(poll.id,))
                )


def embed_instructions(request, poll_id):
    link = request.build_absolute_uri('/approval_polls/{}'.format(poll_id))
    return render(
        request,
        'approval_polls/embed_instructions.html',
        {'link': link}
    )


class CreateView(generic.View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'approval_polls/create.html')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        choices = []
        email_list = []
        choices_links = {}

        if 'question' not in request.POST:
            return render(
                request,
                'approval_polls/create.html',
                {'question_error': 'The question is missing'}
            )
        else:
            question = request.POST['question'].strip()

            if not question:
                return render(
                    request,
                    'approval_polls/create.html',
                    {'question_error': 'The question is missing'}
                )

            c = 1
            name = 'choice1'
            linkname = 'linkurl-choice1'

            while (name in request.POST):
                text = request.POST[name].strip()
                if (text):
                    choices.append(text)
                    if linkname in request.POST:
                        linktext = request.POST[linkname].strip()
                        if linktext:
                            choices_links[text] = linktext
                c += 1
                name = 'choice{}'.format(c)
                linkname = 'linkurl-choice{}'.format(c)

            if not len(choices):
                return render(request, 'approval_polls/create.html', {
                    'choice_error': 'At least one choice is required',
                    'question': question
                })

            # The voting type to be used by the poll
            vtype = request.POST['radio-poll-type']

            if 'close-datetime' in request.POST:
                closedatetime = request.POST['close-datetime']
            else:
                closedatetime = ""

            if closedatetime:
                closedatetime = datetime.datetime.strptime(
                    closedatetime,
                    '%Y/%m/%d %H:%M'
                    )
                current_datetime = timezone.localtime(timezone.now())
                current_tzinfo = current_datetime.tzinfo
                closedatetime = closedatetime.replace(
                    tzinfo=current_tzinfo
                    )
            else:
                closedatetime = None

            if 'show-close-date' in request.POST:
                show_close_date = True
            else:
                show_close_date = False

            if 'show-countdown' in request.POST:
                show_countdown = True
            else:
                show_countdown = False

            if 'show-write-in' in request.POST:
                show_write_in = True
            else:
                show_write_in = False

            if 'show-lead-color' in request.POST:
                show_lead_color = True
            else:
                show_lead_color = False

            if 'public-poll-visibility' in request.POST:
                is_private = False
            else:
                is_private = True

            if vtype == '3':
                # Get all the email Ids to store in the DB.
                emails = request.POST['token-emails']
                for email in emails.split(','):
                    if (re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", email.strip())):
                        email_list.append(email.strip())
                    email_list = list(set(email_list))

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
                is_private=is_private,
            )
            p.save()

            for choice in choices:
                if choice in choices_links:
                    p.choice_set.create(choice_text=choice, choice_link=choices_links[choice])
                else:
                    p.choice_set.create(choice_text=choice)

            # Add in the vote invitation info, if any.
            for email in email_list:
                vi = VoteInvitation(
                    email=email,
                    sent_date=timezone.now(),
                    poll=p,
                    key=VoteInvitation.generate_key(),
                )
                vi.save()
                vi.send_email()

            return HttpResponseRedirect(
                reverse('approval_polls:embed_instructions', args=(p.id,))
            )

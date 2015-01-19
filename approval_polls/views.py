from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from django.contrib.auth.forms import UserCreationForm

from approval_polls.models import Poll, Choice

def index(request):
    poll_list = Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
    paginator = Paginator(poll_list, 10)
    page = request.GET.get('page')
    try:
        polls = paginator.page(page)
    except PageNotAnInteger:
        polls = paginator.page(1)
    except EmptyPage:
        polls = paginator.page(paginator.num_pages)
    return render(request, 'approval_polls/index.html', {"latest_poll_list":polls})

class DetailView(generic.DetailView):
    model = Poll
    template_name = 'approval_polls/detail.html'
    def get_queryset(self):
        """Exclude any polls that aren't published yet."""
        return Poll.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'approval_polls/results.html'

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)

    # TODO: Doesn't handle HTTP_X_FORWARDED_FOR, etc. (Because then you could fake
    # your IP.) We should probably add a config option for when running behind a proxy.
    ballot = p.ballot_set.create(timestamp=timezone.now(),
                                 ip=request.META.get('REMOTE_ADDR'))
    for counter,choice in enumerate(p.choice_set.all()):
        try:
            request.POST['choice'+str(counter+1)]
        except (KeyError):
            pass
        else:
            ballot.vote_set.create(choice=choice)
            ballot.save()
    p.save()
    return HttpResponseRedirect(reverse('approval_polls:results', args=(p.id,)))

def create(request):
    return render(request, 'approval_polls/create.html')

def created(request):
    #if question exists and is not blank, create a new poll p
    error = False
    question = False
    choices = []

    # grab data from request
    # question
    try:
        question = request.POST['question']
    except (KeyError):
        error = True
    # while choice(c) exists and is not blank, add as a choice
    c = 0
    while (True):
        c += 1
        try:
            text = request.POST['choice'+str(c)]
        except (KeyError):
            break
        if (text == ''):
            continue
        choices.append(text)

    if (not question or error or len(choices) == 0):
        message = 'You need a question and at least one choice.'
        return render(request, 'approval_polls/error.html', {'error_message': message})

    p = Poll(question=question, pub_date=timezone.now())
    p.save()

    for choice in choices:
        p.choice_set.create(choice_text=choice)

    #redirect to detail page of your new poll
    #return HttpResponseRedirect(reverse('approval_polls:detail', args=(p.id,)))
    link = request.build_absolute_uri('/approval_polls/' + str(p.id))
    return render(request, 'approval_polls/embed_instructions.html', {'link': link})

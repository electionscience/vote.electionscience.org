from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from approval_polls.models import Poll

def index(request):
  poll_list = Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
  return getPolls(request, poll_list, 'approval_polls/index.html')

@login_required
def myPolls(request):
  poll_list = Poll.objects.filter(pub_date__lte=timezone.now(), user_id=request.user).order_by('-pub_date')
  return getPolls(request, poll_list, 'approval_polls/my_polls.html')

def getPolls(request, poll_list, render_page):
  paginator = Paginator(poll_list, 5)
  page = request.GET.get('page')
  try:
      polls = paginator.page(page)
  except PageNotAnInteger:
      polls = paginator.page(1)
  except EmptyPage:
      polls = paginator.page(paginator.num_pages)
  return render(request, render_page, {'latest_poll_list' : polls})

class DetailView(generic.DetailView):
  model = Poll
  template_name = 'approval_polls/detail.html'
  def get_queryset(self):
      return Poll.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
  model = Poll
  template_name = 'approval_polls/results.html'
  def get_queryset(self):
      return Poll.objects.filter(pub_date__lte=timezone.now())

@require_http_methods(['POST'])
def vote(request, poll_id):
  poll = get_object_or_404(Poll, pk=poll_id)
  ballot = poll.ballot_set.create(timestamp=timezone.now())

  for counter, choice in enumerate(poll.choice_set.all()):
    if 'choice' + str(counter + 1) in request.POST:
      ballot.vote_set.create(choice = choice)
      ballot.save()

  poll.save()

  return HttpResponseRedirect(reverse('approval_polls:results', args=(poll.id,)))

def embed_instructions(request, poll_id):
  link = request.build_absolute_uri('/approval_polls/{}'.format(poll_id))
  return render(request, 'approval_polls/embed_instructions.html', {'link': link})

class CreateView(generic.View):

  @method_decorator(login_required)
  def get(self, request, *args, **kwargs):
    return render(request, 'approval_polls/create.html')

  @method_decorator(login_required)
  def post(self, request, *args, **kwargs):
    choices = []

    if not 'question' in request.POST:
      return render(request, 'approval_polls/create.html', { 'question_error': 'The question is missing' })
    else:
      question = request.POST['question'].strip()

      if not question:
        return render(request, 'approval_polls/create.html', { 'question_error': 'The question is missing' })

      c = 1
      name = 'choice1'

      while (name in request.POST):
        text = request.POST[name].strip()
        if (text): choices.append(text)
        c += 1
        name = 'choice{}'.format(c)

      if not len(choices):
        return render(request, 'approval_polls/create.html', {
          'choice_error': 'At least one choice is required',
          'question': question
          })

      p = Poll(question=question, pub_date=timezone.now(), user=request.user)
      p.save()

      for choice in choices: p.choice_set.create(choice_text=choice)

      return HttpResponseRedirect(reverse('approval_polls:embed_instructions', args=(p.id,)))

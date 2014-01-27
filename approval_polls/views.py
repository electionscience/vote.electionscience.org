from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    for counter,choice in enumerate(p.choice_set.all()):
	try:
		request.POST['choice'+str(counter+1)]
	except (KeyError):
		pass
	else:
		choice.votes += 1
		choice.save()
    p.ballots += 1
    p.save()
    return HttpResponseRedirect(reverse('approval_polls:results', args=(p.id,)))

class CreateView(generic.base.TemplateView):
    template_name = 'approval_polls/create.html'

def created(request):
    #if question exists and is not blank, create a new poll p
    q = request.POST['question']
    if (q == ''):
        #TODO: Tsk, tsk; return some html!
	return HttpResponse('You have to ask a question!')
    p = Poll(question=q, pub_date=timezone.now(), ballots=0)
    p.save();

    #while choice(i) exists and is not blank, add as a choice
    c = 1
    while (True):
        try:
            text = request.POST['choice'+str(c)]
        except (KeyError):
            break
        if (text == ''):
            continue
	p.choice_set.create(choice_text=text, votes=0)
        c += 1

    #redirect to detail page of your new poll
    return HttpResponseRedirect(reverse('approval_polls:detail', args=(p.id,)))

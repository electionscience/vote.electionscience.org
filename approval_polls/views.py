from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from approval_polls.forms.choice_form import ChoiceForm
from approval_polls.forms.poll_form import PollUpdateForm

from approval_polls.models import Poll, Choice


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
    return render(request, render_page, {'latest_poll_list': polls})


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
            ballot.vote_set.create(choice=choice)
            ballot.save()

    poll.save()

    return HttpResponseRedirect(reverse('approval_polls:results', args=(poll.id,)))


def embed_instructions(request, poll_id):
    link = request.build_absolute_uri('/approval_polls/{}'.format(poll_id))
    return render(request, 'approval_polls/embed_instructions.html', {'link': link})


class PollUpdate(generic.View):
    '''A generic update view for our poll.

    Since this is actually a compound form updating two different models
    a Poll and "n" number of Choice instances we cannot use the straight forward
    UpdateView.
    '''


    success_url = '/approval_polls/my-polls'

    @method_decorator(login_required)
    def get(self, request, pk):
        '''We have to get the object and the choices.

        Arguments:
            request (WSGIRequest): the standard request that django calls the get method with
            pk (int): the id of the poll object we are mean to edit

        Returns:
            HTTPResponse
        '''

        form = PollUpdateForm(instance=Poll.objects.get(pk=pk))

        choices = [{'form': ChoiceForm(instance=choice), 'id': choice.id} for choice in Choice.objects.filter(poll__pk=pk)]
        my_context = {'form': form, 'choices': choices}
        request_context = RequestContext(request)

        return render_to_response('approval_polls/poll_update_form.html',
                                  my_context, context_instance=request_context)

    @method_decorator(login_required)
    def post(self, request, pk):
        '''Recieving the updated data for the Poll and it's choices

        Arguments:
            request (WSGIRequest): The request.POST member will contain all the data
            from the form. This must be separated out and validated manually.

            pk (int): The primary key of the Poll being updated.

        Returns:
            WSGIResponse: Upon success it redirects to "my-polls". Upon any failure
            it returns to the poll editing page with the information pre-filled and any
            error messages.
        '''

        # First get the data from the post and sort it out.
        for k in ['question', 'open_date', 'close_date', 'suspended']:
            try:
                poll_data[k] = request.POST.get(k)
            except NameError:
                poll_data = {k: request.POST.get(k)}

        for k in request.POST.keys():
            if k.startswith('choice_text'):
                # We have a choice
                choice_id = k.split('.')[1]
                choice_text = request.POST.get(k)
                try:
                    choices.append({'choice_text': choice_text, 'id': choice_id})
                except NameError:
                    choices = [{'choice_text': choice_text, 'id': choice_id}]

        # Pass the data for the Poll into PollForm and validate it.
        poll_form = PollUpdateForm(data=poll_data, instance=Poll.objects.get(pk=pk))
        poll_valid = poll_form.is_valid()

        # For each Choice pass the data into ChoiceForm and validate.

        try:
            choice_forms = []  # this is ugly but I will do it for now.
            for choice in choices:
                choice_form = ChoiceForm(data={'choice_text': choice['choice_text']},
                                         instance=Choice.objects.get(pk=choice['id']))
                choice_forms.append({'form': choice_form, 'id': choice['id']})
        except NameError:
            pass
            # There are no choices for some reason.

        # check if any of our choices are invalid. Also check if our poll is valid.
        # If any are validated as False we redirect to the poll_form
        if not all([c['form'].is_valid() for c in choice_forms]) or not poll_valid:
            my_context = {'form': poll_form, 'choices': choice_forms}
            request_context = RequestContext(request)
            return render_to_response('approval_polls/poll_update_form.html',
                                      my_context, context_instance=request_context)
        # If there are no errors redirect to my-polls with a friendly message
        # of beauty and success.

        poll_form.save()
        [c['form'].save() for c in choice_forms]  # Just loop through and save the choices
        return HttpResponseRedirect(self.success_url)




class CreateView(generic.View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'approval_polls/create.html')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        choices = []

        if not 'question' in request.POST:
            return render(request, 'approval_polls/create.html', {'question_error': 'The question is missing'})
        else:
            question = request.POST['question'].strip()

            if not question:
                return render(request, 'approval_polls/create.html', {'question_error': 'The question is missing'})

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

            p = Poll(question=question, pub_date=timezone.now(), user=request.user,
                     open_date=timezone.now(), close_date=timezone.now())
            p.save()

            for choice in choices: p.choice_set.create(choice_text=choice)

            return HttpResponseRedirect(reverse('approval_polls:embed_instructions', args=(p.id,)))

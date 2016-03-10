from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    user = models.ForeignKey(User)
    vtype = models.IntegerField(default=2)
    close_date = models.DateTimeField('date closed', null=True, blank=True)
    show_close_date = models.BooleanField(default=False)
    show_countdown = models.BooleanField(default=False)
    show_write_in = models.BooleanField(default=False)
    show_lead_color = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    def is_closed(self):
        if self.close_date:
            return timezone.now() > self.close_date

    def total_ballots(self):
        return self.ballot_set.count()

    def total_votes(self):
        v = 0
        for c in self.choice_set.all():
            v += c.votes()
        return v

    def voters(self):
        v = []
        ballots = self.ballot_set.all()
        for ballot in ballots:
            v.append(ballot.user)
        return v

    def __unicode__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    choice_link = models.CharField(max_length=2048, null=True, blank=True)

    def votes(self):
        return self.vote_set.count()

    def percentage(self):
        if self.poll.total_ballots() == 0:
            return 0
        return self.votes() * 100 / self.poll.total_ballots()

    def __unicode__(self):
        return self.choice_text


class Ballot(models.Model):
    poll = models.ForeignKey(Poll, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    timestamp = models.DateTimeField('time voted')

    def __unicode__(self):
        return self.ip + " at " + str(self.timestamp)


class Vote(models.Model):
    ballot = models.ForeignKey(Ballot)
    choice = models.ForeignKey(Choice)

    def save(self, *args, **kwargs):
        assert self.ballot.poll == self.choice.poll
        super(Vote, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.ballot) + " for " + str(self.choice)


class VoteInvitation(models.Model):
    email = models.EmailField('voter email')
    poll = models.ForeignKey(Poll)
    ballot = models.ForeignKey(Ballot, null=True, blank=True)
    sent_date = models.DateTimeField('invite sent on', null=True, blank=True)
    key = models.CharField('key', max_length=64, unique=True)

    @classmethod
    def generate_key(cls):
        return get_random_string(64)

    def send_email(self, request=None):
        """
        Send the invitation email to the voter.

        """
        email_subject = getattr(
            settings,
            'INVITATION_EMAIL_SUBJECT',
            'approval_polls/invitation_email_subject.txt'
        )
        email_body_html = getattr(
            settings,
            'INVITATION_EMAIL_HTML',
            'approval_polls/invitation_email_body.html'
        )

        ctx_dict = {}
        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)

        current_site = Site.objects.get_current()
        param_string = '?key=' + self.key + '&email=' + self.email
        ctx_dict.update({
            'param_string': param_string,
            'poll': self.poll,
            'site': current_site,
        })

        subject = render_to_string(email_subject, ctx_dict)
        message_html = render_to_string(email_body_html, ctx_dict)
        from_email = settings.DEFAULT_FROM_EMAIL
        email_message = EmailMultiAlternatives(
            subject,
            '',
            from_email,
            [self.email],
        )
        email_message.attach_alternative(message_html, 'text/html')

        email_message.send()

    def __unicode__(self):
        return str(self.email) + " for Poll:" + str(self.poll.id)

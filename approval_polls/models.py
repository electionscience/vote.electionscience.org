import re

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
    pub_date = models.DateTimeField("date published")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vtype = models.IntegerField(default=2)
    close_date = models.DateTimeField("date closed", null=True, blank=True)
    show_close_date = models.BooleanField(default=False)
    show_countdown = models.BooleanField(default=False)
    show_write_in = models.BooleanField(default=False)
    show_lead_color = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    show_email_opt_in = models.BooleanField(default=False)

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

    def can_edit(self):
        return self.total_ballots() == 0

    def add_choices(self, ids, text_data, link_data):
        for n in ids:
            self.choice_set.create(choice_text=text_data[n], choice_link=link_data[n])

    def update_choices(self, ids, text_data, link_data):
        for u in ids:
            c = Choice.objects.get(id=u)
            setattr(c, "choice_text", text_data[u])
            if not (c.choice_link is None and len(link_data[u]) == 0):
                setattr(c, "choice_link", link_data[u])
            c.save()

    def delete_choices(self, ids):
        for d in ids:
            cho_d = Choice.objects.get(id=d)
            cho_d.delete()
            """
              Recommended by RelatedManager, but hasn't worked locally
              self.choice_set.remove(cho_d)
            """

    def send_vote_invitations(self, emails):
        # Get all the email Ids to store in the DB.
        email_list = []
        for email in emails.split(","):
            if re.match(r"([^@|\s]+@[^@]+\.[^@|\s]+)", email.strip()):
                email_list.append(email.strip())
            email_list = list(set(email_list))

        # Add in the vote invitation info, if any.
        for email in email_list:
            vi = VoteInvitation(
                email=email,
                sent_date=timezone.now(),
                poll=self,
                key=VoteInvitation.generate_key(),
            )
            vi.save()
            vi.send_email()

    def invited_emails(self):
        return [str(vi.email) for vi in self.voteinvitation_set.all()]

    def add_tags(self, tags):
        for tagtext in tags:
            text = tagtext.strip().lower()
            if text is not None or text != "":
                tag = PollTag.objects.filter(tag_text=text).first()
                if tag is None:
                    tag = PollTag(tag_text=str(text.strip()))
                    tag.save()
                self.polltag_set.add(tag)

    def delete_tags(self, tags):
        for tagtext in tags:
            tag = PollTag.objects.filter(tag_text=tagtext.strip()).first()
            self.polltag_set.remove(tag)

    def all_tags(self):
        return (",").join([str(t.tag_text) for t in self.polltag_set.all()])

    def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    choice_link = models.CharField(max_length=2048, null=True, blank=True)

    def votes(self):
        return self.vote_set.count()

    def percentage(self):
        if self.poll.total_ballots() == 0:
            return 0
        return self.votes() / self.poll.total_ballots()

    def __unicode__(self):
        return self.choice_text

    def __str__(self):
        return self.choice_text


class Ballot(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField("time voted")
    permit_email = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)

    def __unicode__(self):
        return str(self.id) + " at " + str(self.timestamp)


class Vote(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        assert self.ballot.poll == self.choice.poll
        super(Vote, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.ballot) + " for " + str(self.choice)


class VoteInvitation(models.Model):
    email = models.EmailField("voter email")
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, null=True, blank=True)
    sent_date = models.DateTimeField("invite sent on", null=True, blank=True)
    key = models.CharField("key", max_length=64, unique=True)

    @classmethod
    def generate_key(cls):
        return get_random_string(64)

    def send_email(self, request=None):
        """
        Send the invitation email to the voter.

        """
        email_subject = getattr(
            settings,
            "INVITATION_EMAIL_SUBJECT",
            "approval_polls/invitation_email_subject.txt",
        )
        email_body_html = getattr(
            settings,
            "INVITATION_EMAIL_HTML",
            "approval_polls/invitation_email_body.html",
        )

        ctx_dict = {}
        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)

        current_site = Site.objects.get_current()
        param_string = "?key=" + self.key + "&email=" + self.email
        ctx_dict.update(
            {
                "param_string": param_string,
                "poll": self.poll,
                "site": current_site,
            }
        )

        subject = render_to_string(email_subject, ctx_dict)
        message_html = render_to_string(email_body_html, ctx_dict)
        from_email = settings.DEFAULT_FROM_EMAIL
        email_message = EmailMultiAlternatives(
            subject,
            "",
            from_email,
            [self.email],
        )
        email_message.attach_alternative(message_html, "text/html")

        email_message.send()

    def __unicode__(self):
        return str(self.email) + " for Poll:" + str(self.poll.id)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=5)


class PollTag(models.Model):
    tag_text = models.CharField(max_length=100)
    polls = models.ManyToManyField(Poll)

    @classmethod
    def topTagsPercent(cls, count):
        pollTags = cls.objects.all()
        topTags = sorted(pollTags, key=lambda x: x.polls.count(), reverse=True)[:count]
        sumTotalPolls = sum([t.polls.count() for t in topTags])
        topTagsDict = {}
        for t in topTags:
            topTagsDict[t.tag_text] = float(t.polls.count()) / sumTotalPolls * 100
        return topTagsDict

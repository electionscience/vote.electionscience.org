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
        return Vote.objects.filter(choice__poll=self).count()

    def voters(self):
        return list(self.ballot_set.values_list("user", flat=True).distinct())

    def __unicode__(self):
        return self.question

    def can_edit(self):
        return self.total_ballots() == 0

    def add_choices(self, ids, text_data, link_data):
        for n in ids:
            self.choice_set.create(choice_text=text_data[n], choice_link=link_data[n])

    def update_choices(self, ids, text_data, link_data):
        choices = Choice.objects.filter(id__in=ids)
        for choice in choices:
            choice.choice_text = text_data[choice.id]
            if not (choice.choice_link is None and len(link_data[choice.id]) == 0):
                choice.choice_link = link_data[choice.id]
        Choice.objects.bulk_update(choices, ["choice_text", "choice_link"])

    def delete_choices(self, ids):
        Choice.objects.filter(id__in=ids, poll=self).delete()

    def send_vote_invitations(self, emails):
        # Get unique valid email addresses
        email_list = {
            email.strip()
            for email in emails.split(",")
            if re.match(r"([^@|\s]+@[^@]+\.[^@|\s]+)", email.strip())
        }

        # Create all invitations at once
        now = timezone.now()
        invitations = [
            VoteInvitation(
                email=email, sent_date=now, poll=self, key=VoteInvitation.generate_key()
            )
            for email in email_list
        ]
        created_invitations = VoteInvitation.objects.bulk_create(invitations)

        # Send emails after creation
        for invitation in created_invitations:
            invitation.send_email()

    def invited_emails(self):
        return list(self.voteinvitation_set.values_list("email", flat=True))

    def add_tags(self, tags):
        for tagtext in tags:
            text = tagtext.strip().lower()
            if text is not None:
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
        from django.db.models import CharField, Value
        from django.db.models.functions import Concat

        return (
            self.polltag_set.annotate(
                str_tag_text=Cast("tag_text", CharField())
            ).aggregate(
                tags=Concat("str_tag_text", output_field=CharField(), separator=",")
            )[
                "tags"
            ]
            or ""
        )

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
    timestamp = models.DateTimeField("time voted", auto_now_add=True)
    permit_email = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)

    def __unicode__(self):
        return str(self.id) + " at " + str(self.timestamp)


class Vote(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.ballot.poll != self.choice.poll:
            raise ValueError("The ballot and choice must belong to the same poll.")
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
        from django.db.models import Count, F, FloatField
        from django.db.models.functions import Cast

        # Get top tags with their poll counts
        top_tags = cls.objects.annotate(poll_count=Count("polls")).order_by(
            "-poll_count"
        )[:count]

        # Calculate total polls for percentage
        total_polls = sum(tag.poll_count for tag in top_tags)

        # Calculate percentages
        return (
            {tag.tag_text: (tag.poll_count / total_polls * 100) for tag in top_tags}
            if total_polls > 0
            else {}
        )

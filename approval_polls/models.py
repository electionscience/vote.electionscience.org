from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone


class Poll(models.Model):
    '''A Poll class. This is the top level container for a Poll.

    referenced by Choices model and the Ballot model
    '''

    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    user = models.ForeignKey(User)
    open_date = models.DateField()
    close_date = models.DateField()
    suspended = models.BooleanField(default=False)

    def is_closed(self):
        '''Determine if the poll is open or closed

        Arguments:
            None

        Returns:
            boolean: True if the close_date < datetime.datetime.now()
                     otherwise False
        '''

        now = timezone.now()
        # If now is greater than the close date the close date is in the past and will return True
        # If self.close_date is greater than now then close date is in the future and this returns False
        return now > self.close_date

    def total_ballots(self):
        '''Get the ballot count for this poll

        Arguments:
            None

        Returns:
            int: where int is the number of ballots cast on this poll
        '''

        # Django gives us a handy way to access our relationships by '_set'
        # we leverage that here.
        return self.ballot_set.count()

    def total_votes(self):
        '''Get the total votes for this poll

        Arguments:
            None

        Returns:
            int: Total number of votes
        '''

        v = 0
        for c in self.choice_set.all():
            v += c.votes()
        return v

    def __unicode__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)

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

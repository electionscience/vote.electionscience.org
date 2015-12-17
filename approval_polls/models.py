from django.contrib.auth.models import User
from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    user = models.ForeignKey(User)
    vtype = models.IntegerField(default=2)

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

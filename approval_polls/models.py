from django.db import models

class Poll(models.Model):
	question = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')
	ballots = models.IntegerField(default=0)
	def total_votes(self):
		v = 0
		for c in self.choice_set.all():
			v += c.votes
		return v
	def __unicode__(self):
		return self.question

class Choice(models.Model):
	poll = models.ForeignKey(Poll)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)
	def percentage(self):
		if self.poll.ballots == 0:
			return 0
		return self.votes*100/self.poll.ballots
	def __unicode__(self):
		return self.choice_text

#TODO: Use these to better-track who's voting
#class Ballot(models.Model):
#	poll = models.ForeignKey(Poll)
#	timestamp = models.DateTimeField('time voted')
#	ip = models.GenericIPAddressField()
#	def __unicode__(self):
#		return self.ip + " at " + self.timestamp
#
#class Vote(models.Model):
#	ballot = models.ForeignKey(Ballot)
#	choice = models.ForeignKey(Choice)
#	def __unicode__(self):
#		return self.ballot + " for " + self.choice


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0009_poll_show_lead_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoteInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, verbose_name=b'voter email')),
                ('sent_date', models.DateTimeField(null=True, verbose_name=b'invite sent on', blank=True)),
                ('key', models.CharField(unique=True, max_length=64, verbose_name=b'key')),
                ('ballot', models.ForeignKey(blank=True, to='approval_polls.Ballot', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='poll',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='voteinvitation',
            name='poll',
            field=models.ForeignKey(to='approval_polls.Poll'),
        ),
    ]

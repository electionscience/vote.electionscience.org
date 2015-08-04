# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0002_poll_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='close_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 3, 20, 45, 20, 377257, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='poll',
            name='open_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 3, 20, 45, 34, 326601, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

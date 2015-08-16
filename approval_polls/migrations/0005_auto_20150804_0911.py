# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0004_auto_20150803_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='close_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 4, 16, 11, 0, 208090, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='poll',
            name='open_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 4, 16, 11, 11, 228459, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0004_poll_vtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='close_date',
            field=models.DateTimeField(null=True, verbose_name=b'date closed', blank=True),
        ),
    ]

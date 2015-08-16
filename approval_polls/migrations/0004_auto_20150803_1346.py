# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0003_auto_20150803_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='close_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='open_date',
            field=models.DateTimeField(null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0005_auto_20150804_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='close_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='poll',
            name='open_date',
            field=models.DateField(),
        ),
    ]

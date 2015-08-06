# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0006_auto_20150804_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='suspended',
            field=models.BooleanField(default=False),
        ),
    ]

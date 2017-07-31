# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0012_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
    ]

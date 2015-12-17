# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0003_ballot_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='vtype',
            field=models.IntegerField(default=2),
        ),
    ]

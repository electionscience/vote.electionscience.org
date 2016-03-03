# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0010_voteinvitation_poll_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='choice_link',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0006_poll_show_close_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='show_countdown',
            field=models.BooleanField(default=False),
        ),
    ]

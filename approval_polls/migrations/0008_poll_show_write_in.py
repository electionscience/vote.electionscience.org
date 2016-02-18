# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0007_poll_show_countdown'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='show_write_in',
            field=models.BooleanField(default=False),
        ),
    ]

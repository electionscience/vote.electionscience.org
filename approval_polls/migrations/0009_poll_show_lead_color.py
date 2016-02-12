# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approval_polls', '0008_poll_show_write_in'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='show_lead_color',
            field=models.BooleanField(default=False),
        ),
    ]

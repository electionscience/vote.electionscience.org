# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_polls", "0017_ballot_remove_unique_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ballot",
            name="timestamp",
            field=models.DateTimeField(verbose_name="time voted"),
        ),
        migrations.AlterField(
            model_name="poll",
            name="close_date",
            field=models.DateTimeField(
                null=True, verbose_name="date closed", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="poll",
            name="pub_date",
            field=models.DateTimeField(verbose_name="date published"),
        ),
        migrations.AlterField(
            model_name="voteinvitation",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="voter email"),
        ),
        migrations.AlterField(
            model_name="voteinvitation",
            name="key",
            field=models.CharField(unique=True, max_length=64, verbose_name="key"),
        ),
        migrations.AlterField(
            model_name="voteinvitation",
            name="sent_date",
            field=models.DateTimeField(
                null=True, verbose_name="invite sent on", blank=True
            ),
        ),
    ]

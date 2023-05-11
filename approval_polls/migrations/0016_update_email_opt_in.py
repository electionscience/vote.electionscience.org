# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_polls", "0015_email_opt_in"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vote",
            name="email",
        ),
        migrations.RemoveField(
            model_name="vote",
            name="permit_email",
        ),
        migrations.AddField(
            model_name="ballot",
            name="email",
            field=models.EmailField(max_length=254, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="ballot",
            name="permit_email",
            field=models.BooleanField(default=False),
        ),
    ]

# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_polls", "0014_polltag"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="show_email_opt_in",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vote",
            name="email",
            field=models.EmailField(max_length=254, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="vote",
            name="permit_email",
            field=models.BooleanField(default=False),
        ),
    ]

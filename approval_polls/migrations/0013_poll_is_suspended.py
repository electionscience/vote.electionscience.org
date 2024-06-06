# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_polls", "0012_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="is_suspended",
            field=models.BooleanField(default=False),
        ),
    ]

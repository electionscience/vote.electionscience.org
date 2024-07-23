# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("approval_polls", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="user",
            field=models.ForeignKey(
                on_delete=models.CASCADE, default=0, to=settings.AUTH_USER_MODEL
            ),
            preserve_default=False,
        ),
    ]

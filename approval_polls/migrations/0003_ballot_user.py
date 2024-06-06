# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("approval_polls", "0002_poll_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballot",
            name="user",
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

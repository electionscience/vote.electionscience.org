# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("approval_polls", "0011_choice_choice_link"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("zipcode", models.CharField(max_length=5)),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

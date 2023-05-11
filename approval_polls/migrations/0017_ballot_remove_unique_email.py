# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approval_polls", "0016_update_email_opt_in"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ballot",
            name="email",
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]

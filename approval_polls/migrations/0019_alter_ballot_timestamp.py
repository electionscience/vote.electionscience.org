# Generated by Django 5.0.7 on 2024-07-23 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("approval_polls", "0018_auto_20230511_0246"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ballot",
            name="timestamp",
            field=models.DateTimeField(auto_now_add=True, verbose_name="time voted"),
        ),
    ]
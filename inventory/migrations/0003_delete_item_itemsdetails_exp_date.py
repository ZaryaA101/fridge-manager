# Generated by Django 5.2 on 2025-04-08 05:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_family_itemsdetails_fridgecontent_familytag"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Item",
        ),
        migrations.AddField(
            model_name="itemsdetails",
            name="exp_date",
            field=models.DateField(
                default=datetime.datetime(
                    2025, 4, 15, 5, 7, 30, 720292, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Expiration date",
            ),
        ),
    ]

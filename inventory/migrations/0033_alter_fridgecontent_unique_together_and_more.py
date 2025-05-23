# Generated by Django 5.2 on 2025-05-07 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0032_alter_userprofile_user"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="fridgecontent",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="fridgecontent",
            name="item_description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="itemsdetails",
            name="item_quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name="fridgecontent",
            unique_together={
                (
                    "family_id",
                    "compartment_id",
                    "item_id",
                    "expiration_date",
                    "quantity",
                    "item_description",
                )
            },
        ),
    ]

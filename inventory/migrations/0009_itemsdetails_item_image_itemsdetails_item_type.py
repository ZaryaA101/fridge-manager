# Generated by Django 5.2 on 2025-04-12 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0008_rename_fridgedetails_fridgedetail"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemsdetails",
            name="item_image",
            field=models.ImageField(blank=True, upload_to=""),
        ),
        migrations.AddField(
            model_name="itemsdetails",
            name="item_type",
            field=models.CharField(max_length=30, null=True),
        ),
    ]

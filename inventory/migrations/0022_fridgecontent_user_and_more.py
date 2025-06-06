# Generated by Django 4.2.20 on 2025-04-25 01:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0021_alter_fridgecontent_family_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='fridgecontent',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='fridgecontent',
            name='compartment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FridgeContent', to='inventory.compartmentsdetails'),
        ),
        migrations.AlterField(
            model_name='fridgecontent',
            name='family_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FridgeContent', to='inventory.family'),
        ),
        migrations.AlterField(
            model_name='fridgecontent',
            name='item_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FridgeContent', to='inventory.itemsdetails'),
        ),
    ]

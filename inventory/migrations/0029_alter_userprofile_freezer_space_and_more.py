# Generated by Django 4.2.20 on 2025-05-04 23:04

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='freezer_space',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='leftdoor_space',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='overall_space',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='producebin_space',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='rightdoor_space',
            field=models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]

# Generated by Django 2.2 on 2020-06-29 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Class', '0002_auto_20200320_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classwhichdivision',
            name='which_division',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

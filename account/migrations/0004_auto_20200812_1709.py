# Generated by Django 2.2 on 2020-08-12 11:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.ImageField(upload_to=''), null=True, size=None),
        ),
    ]

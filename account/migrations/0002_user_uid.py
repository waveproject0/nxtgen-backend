# Generated by Django 2.2 on 2020-06-30 11:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Public identifier'),
        ),
    ]
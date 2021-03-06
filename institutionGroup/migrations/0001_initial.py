# Generated by Django 2.2 on 2020-03-20 17:37

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('institution', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstitutionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('geolocation', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=2, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupInstitutionRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institution.Institution')),
                ('institutional_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institutionGroup.InstitutionGroup')),
            ],
            options={
                'unique_together': {('institutional_group', 'institution')},
            },
        ),
    ]

# Generated by Django 2.2 on 2020-03-20 17:37

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorityRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BoardAffiliation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('acroname', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='InstituteType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('FRML', 'Formal'), ('NFRML', 'NonFormal')], max_length=5)),
                ('Type', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('geolocation', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=2, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionStudentRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionTeacherRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authority_role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='institution.AuthorityRole')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institution.Institution')),
            ],
        ),
        migrations.CreateModel(
            name='SuperAdminControl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('institution_teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='institution.InstitutionTeacherRelation')),
            ],
        ),
    ]
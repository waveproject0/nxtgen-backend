# Generated by Django 2.2 on 2020-06-29 05:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
        ('nxtgenUser', '0001_initial'),
        ('commentExplanation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('edited_version', models.BooleanField(default=False)),
                ('it_self', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='concept.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='ConceptExplanation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concept.Concept')),
                ('explanation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Explanation')),
            ],
        ),
        migrations.CreateModel(
            name='ConceptSubjectRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concept.Concept')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Subject')),
            ],
            options={
                'unique_together': {('subject', 'concept')},
            },
        ),
        migrations.CreateModel(
            name='ConceptEdit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nxtgenUser.NxtgenUser')),
                ('edited_concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concept.Concept')),
            ],
            options={
                'unique_together': {('edited_concept', 'approved_by')},
            },
        ),
        migrations.CreateModel(
            name='ConceptApprovedEdit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='concept.Concept')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nxtgenUser.NxtgenUser')),
            ],
            options={
                'unique_together': {('concept', 'user')},
            },
        ),
    ]

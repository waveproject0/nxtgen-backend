# Generated by Django 2.2 on 2020-06-29 05:11

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nxtgenUser', '0001_initial'),
        ('Class', '0003_auto_20200629_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('acroname', models.CharField(max_length=10)),
                ('exam_level', models.CharField(choices=[('primary', 'primary'), ('high', 'High'), ('higher secondery', 'Higher secondery'), ('ug', 'UG'), ('pg', 'PG'), ('phd', 'PHD'), ('research', 'Research')], max_length=20)),
                ('exam_type', models.CharField(choices=[('academic', 'Academic'), ('compitative', 'compitative'), ('entrance', 'Entrance'), ('job selection', 'Job selection')], max_length=20)),
                ('exam_spread', models.CharField(choices=[('local', 'Local'), ('national', 'Nationl'), ('international', 'International')], max_length=20)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('official_link', models.URLField(blank=True, max_length=500, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExamApprovedEdit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ExamFollowerRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ExamPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publish', models.DateTimeField(auto_now_add=True)),
                ('block_comment', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExamPostComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExamQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publish', models.DateTimeField(auto_now_add=True)),
                ('block_comment', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExamQueryComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExamQueryExplanation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active')], default='draft', max_length=20)),
                ('publish', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExamQueryExplanationComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archive', 'Archived')], default='draft', max_length=20)),
                ('class_subject_type', models.CharField(choices=[('none', 'None'), ('subject', 'Subject'), ('additional subject', 'Additional subject')], max_length=20)),
                ('test_type', models.CharField(choices=[('subjective', 'Subjective'), ('objective', 'Objective')], max_length=20)),
                ('marking', models.BooleanField(default=False)),
                ('negative_marking', models.BooleanField(default=False)),
                ('public', models.BooleanField(default=True)),
                ('publish', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ans_choices', models.BooleanField(default=False)),
                ('positive_marks', models.PositiveIntegerField(blank=True, null=True)),
                ('negative_marks', models.PositiveIntegerField(blank=True, null=True)),
                ('position', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TestQuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=500)),
                ('correct', models.BooleanField(default=False)),
                ('test_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.TestQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='TestStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_type', models.CharField(choices=[('none', 'None'), ('subject', 'Subject'), ('additional subject', 'Additional subject')], max_length=20)),
                ('additional_subject_student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassStudentAdditionalSubjectTeacherRelation')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nxtgenUser.NxtgenUser')),
                ('subject_student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassStudentSubjectTeacherRelation')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.Test')),
            ],
        ),
        migrations.CreateModel(
            name='TestStudentAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_in_minute', models.DurationField()),
                ('total_marks', models.IntegerField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('test_student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='exam.TestStudent')),
            ],
        ),
        migrations.CreateModel(
            name='TestSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(max_length=100)),
                ('position', models.PositiveIntegerField()),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.Test')),
            ],
        ),
        migrations.CreateModel(
            name='TestQuestionStudentExplanation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('explanation', django.contrib.postgres.fields.jsonb.JSONField()),
                ('attempted_student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.TestStudentAttempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.TestQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='TestQuestionStudentChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempted_student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.TestStudentAttempt')),
                ('question_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.TestQuestionChoice')),
            ],
        ),
    ]
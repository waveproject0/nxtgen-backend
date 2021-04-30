# Generated by Django 2.2 on 2020-03-20 17:37

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Class', '0001_initial'),
        ('nxtgenUser', '0001_initial'),
        ('post', '0001_initial'),
        ('commentExplanation', '0001_initial'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Class', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Class.Class')),
            ],
        ),
        migrations.CreateModel(
            name='TopicFormQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('archive', 'Archived')], default='active', max_length=20)),
                ('subject_type', models.CharField(choices=[('subject', 'Subject'), ('additional subject', 'Additional subject')], max_length=20)),
                ('publish', models.DateTimeField(auto_now_add=True)),
                ('archive_date', models.DateField()),
                ('additional_subject_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.AdditionalSubjectTeacherRelation')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassStudentRelation')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.Form')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='post.Post')),
                ('subject_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassSubjectTeacherRelation')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.SubjectTopicRelation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubTopicFormQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('archive', 'Archived')], default='active', max_length=20)),
                ('subject_type', models.CharField(choices=[('subject', 'Subject'), ('additional subject', 'Additional subject')], max_length=20)),
                ('publish', models.DateTimeField(auto_now_add=True)),
                ('archive_date', models.DateField()),
                ('additional_subject_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.AdditionalSubjectTeacherRelation')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassStudentRelation')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.Form')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='post.Post')),
                ('sub_topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.TopicSubTopicRelation')),
                ('subject_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassSubjectTeacherRelation')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('archive', 'Archived')], default='active', max_length=20)),
                ('post_type', models.CharField(choices=[('class', 'Class only'), ('educational', 'Educational'), ('informational', 'Informational'), ('news', 'News')], default='class', max_length=20)),
                ('subject_type', models.CharField(choices=[('subject', 'Subject'), ('additional subject', 'Additional subject')], max_length=20)),
                ('block_comment', models.BooleanField(default=False)),
                ('public', models.BooleanField(default=False)),
                ('publish', models.DateTimeField(auto_now_add=True)),
                ('archive_date', models.DateField()),
                ('additional_subject_teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.AdditionalSubjectTeacherRelation')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nxtgenUser.NxtgenUser')),
                ('form', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='form.Form')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='post.Post')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Subject')),
                ('subject_teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassSubjectTeacherRelation')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='ExplanationTopicFormQueryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archive', 'Archived')], default='draft', max_length=20)),
                ('publish', models.DateTimeField(blank=True, null=True)),
                ('explanation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Explanation')),
                ('topic_form_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.TopicFormQuery')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExplanationSubTopicFormQueryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archive', 'Archived')], default='draft', max_length=20)),
                ('publish', models.DateTimeField(blank=True, null=True)),
                ('explanation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Explanation')),
                ('subTopic_form_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.SubTopicFormQuery')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentTopicFormQueryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Comment')),
                ('topic_form_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.TopicFormQuery')),
            ],
        ),
        migrations.CreateModel(
            name='CommentSubTopicFormQueryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Comment')),
                ('subTopic_form_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.SubTopicFormQuery')),
            ],
        ),
        migrations.CreateModel(
            name='CommentFormPostRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commentExplanation.Comment')),
                ('form_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='form.FormPost')),
            ],
        ),
    ]

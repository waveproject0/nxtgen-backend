# Generated by Django 2.2 on 2020-03-20 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Class', '0001_initial'),
        ('institution', '0001_initial'),
        ('course', '0001_initial'),
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsubjectteacherrelation',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='institution.InstitutionTeacherRelation'),
        ),
        migrations.AddField(
            model_name='classstudentsubjectteacherrelation',
            name='class_student_relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassStudentRelation'),
        ),
        migrations.AddField(
            model_name='classstudentsubjectteacherrelation',
            name='class_subject_teacher_relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassSubjectTeacherRelation'),
        ),
        migrations.AddField(
            model_name='classstudentrelation',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassSectionRelation'),
        ),
        migrations.AddField(
            model_name='classstudentrelation',
            name='session_start_date',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.SessionStartDate'),
        ),
        migrations.AddField(
            model_name='classstudentrelation',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='institution.InstitutionStudentRelation'),
        ),
        migrations.AddField(
            model_name='classstudentadditionalsubjectteacherrelation',
            name='class_additional_subject_teacher_relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.AdditionalSubjectTeacherRelation'),
        ),
        migrations.AddField(
            model_name='classstudentadditionalsubjectteacherrelation',
            name='class_student_relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassStudentRelation'),
        ),
        migrations.AddField(
            model_name='classsectionrelation',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='institution.InstitutionTeacherRelation'),
        ),
        migrations.AddField(
            model_name='classsectionrelation',
            name='which_division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassWhichDivision'),
        ),
        migrations.AlterUniqueTogether(
            name='classdivision',
            unique_together={('duration', 'total_divisions')},
        ),
        migrations.AddField(
            model_name='class',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.Course'),
        ),
        migrations.AddField(
            model_name='class',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='department.Department'),
        ),
        migrations.AddField(
            model_name='class',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Class.ClassDivision'),
        ),
        migrations.AddField(
            model_name='class',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institution.Institution'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='institution.InstitutionTeacherRelation'),
        ),
        migrations.AddField(
            model_name='additionalsubjectteacherrelation',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.ClassSectionRelation'),
        ),
        migrations.AddField(
            model_name='additionalsubjectteacherrelation',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.AdditionalSubject'),
        ),
        migrations.AddField(
            model_name='additionalsubjectteacherrelation',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='institution.InstitutionTeacherRelation'),
        ),
        migrations.AddField(
            model_name='additionalsubject',
            name='Class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Class.Class'),
        ),
        migrations.AddField(
            model_name='additionalsubject',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Subject'),
        ),
        migrations.AlterUniqueTogether(
            name='classwhichdivision',
            unique_together={('Class', 'which_division')},
        ),
        migrations.AlterUniqueTogether(
            name='classsubjectteacherrelation',
            unique_together={('section', 'subject'), ('section', 'teacher')},
        ),
        migrations.AlterUniqueTogether(
            name='classstudentsubjectteacherrelation',
            unique_together={('class_student_relation', 'class_subject_teacher_relation')},
        ),
        migrations.AlterUniqueTogether(
            name='classstudentadditionalsubjectteacherrelation',
            unique_together={('class_student_relation', 'class_additional_subject_teacher_relation')},
        ),
        migrations.AlterUniqueTogether(
            name='classsectionrelation',
            unique_together={('section', 'which_division')},
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('institution', 'course')},
        ),
        migrations.AlterUniqueTogether(
            name='additionalsubjectteacherrelation',
            unique_together={('section', 'subject'), ('section', 'teacher')},
        ),
        migrations.AlterUniqueTogether(
            name='additionalsubject',
            unique_together={('Class', 'subject')},
        ),
    ]

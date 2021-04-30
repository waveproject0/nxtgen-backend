from graphql_relay import from_global_id
from graphql import GraphQLError
from django.db.models.signals import post_save

from django.db import models
from django.contrib.postgres.fields import ArrayField
from institution.models import Institution, InstitutionTeacherRelation, InstitutionStudentRelation
from course.models import Course, Subject, CourseSubjectRelation
from department.models import Department
from studentProfile.models import StudentProfile
from teacherProfile.models import TeacherProfile




class Class(models.Model):
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
	alias = models.CharField(max_length=100, null=True, blank=True)
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
	teacher = models.ForeignKey(InstitutionTeacherRelation, on_delete=models.SET_NULL, null=True, blank=True)
	division = models.ForeignKey('ClassDivision', on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		unique_together = ("institution", "course")

	def __str__(self):
		return self.institution.name +" / "+ self.course.name


class AdditionalSubject(models.Model):
	SUBJECT_TYPE = (
			('open elective','Open elective'),
			('core elective','Core elective'),
			('additional subject','Additional subject')
		)
	Class = models.ForeignKey('Class', on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	subject_type = models.CharField(max_length=50, choices=SUBJECT_TYPE, default='additional subject')

	class Meta:
		unique_together = ("Class", "subject")

	def __str__(self):
		return self.Class.institution.name +" / "+ self.subject.name +" / "+ self.subject_type


		
class ClassDivision(models.Model):
	duration = models.PositiveIntegerField()
	total_divisions = models.PositiveIntegerField()
	name = models.CharField(max_length=20)

	class Meta:
		unique_together = ("duration", "total_divisions")

	def __str__(self):
		return self.name +" / "+ str(self.total_divisions) +" / "+ str(self.duration)



class ClassWhichDivision(models.Model):
	Class = models.ForeignKey('Class', on_delete=models.CASCADE)
	which_division = models.PositiveIntegerField(default=0)
	no_section = models.BooleanField(default=False)

	class Meta:
		unique_together = ("Class", "which_division")

	def __str__(self):
		return self.Class.course.name +" / "+ str(self.which_division) +" / "+ self.no_section

class ClassSectionRelation(models.Model):
	which_division = models.ForeignKey('ClassWhichDivision',models.CASCADE)
	section = models.CharField(max_length=50, blank=True, default='SECTION 0')
	teacher = models.ForeignKey(InstitutionTeacherRelation, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		unique_together = ("section", "which_division")

	def __str__(self):
		return self.which_division.Class.course.name +" / "+ str(self.which_division.which_division) +" / "+ self.section


class SessionStartDate(models.Model):
	start_date = models.DateField(auto_now=False, auto_now_add=False)

	def __str__(self):
		return str(self.start_date)



class ClassStudentRelation(models.Model):
	student = models.OneToOneField(InstitutionStudentRelation, on_delete=models.CASCADE)
	section = models.ForeignKey('ClassSectionRelation', on_delete=models.CASCADE)
	session_start_date = models.ForeignKey('SessionStartDate', on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.section.section +" / "+ self.student.student.student.nxtgen_user.email


class AbstractSubjectTeacher(models.Model):
	teacher = models.ForeignKey(InstitutionTeacherRelation, on_delete=models.SET_NULL, null=True)
	section = models.ForeignKey('ClassSectionRelation', on_delete=models.CASCADE)

	class Meta:
		abstract = True



class ClassSubjectTeacherRelation(AbstractSubjectTeacher):
	subject = models.ForeignKey(CourseSubjectRelation, on_delete=models.CASCADE)
	
	class Meta:
		unique_together = (("section", "subject"),('section', "teacher"))

	def __str__(self):
		return self.section.section +" / "+ self.subject.subject.name +" / "+ self.teacher.teacher.teacher.nxtgen_user.email +" / "+ self.position


class AdditionalSubjectTeacherRelation(AbstractSubjectTeacher):
	subject = models.ForeignKey(AdditionalSubject, on_delete=models.CASCADE)
	
	class Meta:
		unique_together = (("section", "subject"),('section', "teacher"))

	def __str__(self):
		return self.section.section +" / "+ self.subject.subject.name +" / "+ self.teacher.teacher.teacher.nxtgen_user.email


class ClassStudentSubjectTeacherRelation(models.Model):
	class_student_relation = models.ForeignKey('ClassStudentRelation', on_delete=models.CASCADE)
	class_subject_teacher_relation = models.ForeignKey('ClassSubjectTeacherRelation', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("class_student_relation", "class_subject_teacher_relation")


	def __str__(self):
		return self.class_student_relation.student.student.student.nxtgen_user.email +" / "+ self.class_subject_teacher_relation.subject.subject.name +" / "+ self.class_subject_teacher_relation.teacher.teacher.teacher.nxtgen_user.email

def create_ClassStudentSubjectTeacher(sender, **kwargs):
    if kwargs['created']:
        if hasattr(kwargs['instance'], '_subject_teacher'):
            for section_subject_teacher in kwargs['instance']._subject_teacher:
                section_subject_teacher_obj = ClassSubjectTeacherRelation.objects.get(
                    id=from_global_id(section_subject_teacher)[1]
                    )

                ClassStudentSubjectTeacherRelation.objects.create(
                    class_student_relation=kwargs['instance'],class_subject_teacher_relation=section_subject_teacher_obj
                    )

        else:
            section_subject_teachers = ClassSubjectTeacherRelation.objects.filter(
                section=kwargs['instance'].section
                )
            for section_subject_teacher_obj in section_subject_teachers:
            	ClassStudentSubjectTeacherRelation.objects.create(
                    class_student_relation=kwargs['instance'],class_subject_teacher_relation=section_subject_teacher_obj
                	)


post_save.connect(create_ClassStudentSubjectTeacher, sender=ClassStudentRelation, weak=False)




class ClassStudentAdditionalSubjectTeacherRelation(models.Model):
	class_student_relation = models.ForeignKey('ClassStudentRelation', on_delete=models.CASCADE)
	class_additional_subject_teacher_relation = models.ForeignKey('AdditionalSubjectTeacherRelation', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("class_student_relation", "class_additional_subject_teacher_relation")


	def __str__(self):
		return self.class_student_relation.student.student.student.nxtgen_user.email +" / "+ self.class_additional_subject_teacher_relation.subject.subject.name +" / "+ self.class_additional_subject_teacher_relation.teacher.teacher.teacher.nxtgen_user.email


def create_ClassStudentAdditionalSubjectTeacher(sender, **kwargs):
    if kwargs['created']:
        if hasattr(kwargs['instance'], '_additional_subject_teacher'):
            for section_additional_subject_teacher in kwargs['instance']._additional_subject_teacher:
                section_additional_subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.get(
                    id=from_global_id(section_additional_subject_teacher)[1]
                    )

                ClassStudentAdditionalSubjectTeacherRelation.objects.create(
                    class_student_relation=kwargs['instance'],class_additional_subject_teacher_relation=section_additional_subject_teacher_obj
                    )

        else:
            additional_subject_teachers = AdditionalSubjectTeacherRelation.objects.filter(
                section=kwargs['instance'].section
                )
            for section_additional_subject_teacher_obj in additional_subject_teachers:
                ClassStudentAdditionalSubjectTeacherRelation.objects.create(
                    class_student_relation=kwargs['instance'],class_additional_subject_teacher_relation=section_additional_subject_teacher_obj
                    )



post_save.connect(create_ClassStudentAdditionalSubjectTeacher, sender=ClassStudentRelation, weak=False)
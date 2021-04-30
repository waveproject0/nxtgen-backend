from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from Class.models import ClassStudentRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation



class AbstractAttendance(models.Model):
	ATTENDANCE_TYPE = (
		('class', 'Class'),
		('internal exam', 'Internal exam'),
		('external exam', 'External exam')
		)

	date = models.DateField(auto_now=True, auto_now_add=False)
	attendance_for = models.CharField(max_length=50, choices=ATTENDANCE_TYPE)

	class Meta:
		abstract = True


class SubjectTeacherAttendance(AbstractAttendance):
	teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("teacher","date")

	def __str__(self):
		return self.teacher.teacher.teacher.teacher.nxtgen_user.email +" / "+ str(self.date)


class AdditionalSubjectTeacherAttendance(AbstractAttendance):
	teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("teacher","date")

	def __str__(self):
		return self.teacher.teacher.teacher.teacher.nxtgen_user.email +" / "+ str(self.date)






class AbstractAttendee(models.Model):
	attendee = models.ForeignKey(ClassStudentRelation, on_delete=models.CASCADE)

	class Meta:
		abstract = True


class SubjectAttendee(AbstractAttendee):
	attendance = models.ForeignKey('SubjectTeacherAttendance', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("attendance","attendee")

	def __str__(self):
		return str(self.attendance.date) +" / "+ self.attendee.student.student.student.nxtgen_user.email


def create_subject_attendee(sender, **kwargs):
	if kwargs['created']:
		for attendee in kwargs['instance']._attendee_obj_array:
			SubjectAttendee.objects.create(attendance=kwargs['instance'],attendee=attendee)


post_save.connect(create_subject_attendee, sender=SubjectTeacherAttendance, weak=False)


class AdditionalSubjectAttendee(AbstractAttendee):
	attendance = models.ForeignKey('AdditionalSubjectTeacherAttendance', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("attendance","attendee")

	def __str__(self):
		return str(self.attendance.date) +" / "+ self.attendee.student.student.student.nxtgen_user.email


def create_additional_subject_attendee(sender, **kwargs):
	if kwargs['created']:
		for attendee in kwargs['instance']._attendee_obj_array:
			AdditionalSubjectAttendee.objects.create(attendance=kwargs['instance'],attendee=attendee)


post_save.connect(create_subject_attendee, sender=AdditionalSubjectTeacherAttendance, weak=False)


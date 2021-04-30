from django.db import models
from django.contrib.postgres.fields import ArrayField
from teacherProfile.models import TeacherProfile
from studentProfile.models import StudentProfile


class BoardAffiliation(models.Model):
	name = models.CharField(max_length=50, unique=True)
	acroname = models.CharField(max_length=20)


	def __str__(self):
		return self.acroname


class InstituteType(models.Model):
	institution_status = (('FRML', 'Formal'),('NFRML', 'NonFormal'),)

	status = models.CharField(max_length=5, choices=institution_status)
	Type = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.Type

class AuthorityRole(models.Model):
	role = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.role

class Institution(models.Model):
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	geolocation = ArrayField(models.FloatField(), size=2, unique=True)
	board_affiliation = models.ForeignKey('BoardAffiliation', on_delete=models.SET_NULL, blank=True, null=True)
	institute_type = models.ForeignKey('InstituteType', on_delete=models.SET_NULL, blank=True, null=True)

	def __str__(self):
		return self.name


class InstitutionTeacherRelation(models.Model):
	institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
	teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
	authority_role = models.ForeignKey('AuthorityRole', on_delete=models.SET_NULL, null=True)

	class Meta:
		unique_together = ("teacher", "institution")

	def __str__(self):
		return self.institution.name + " / " + self.teacher.teacher.nxtgen_user.email

class InstitutionStudentRelation(models.Model):
	institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
	student =  models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("student", "institution")

	def __str__(self):
		return self.institution.name + " / " + self.student.student.nxtgen_user.email


class SuperAdminControl(models.Model):
	institution_teacher = models.OneToOneField('InstitutionTeacherRelation', on_delete=models.CASCADE)
	status = models.BooleanField(default=True)

	def __str__(self):
		return self.institution_teacher.authority_role.role + " / " + str(self.status)

from django.db import models
from django.db.models.signals import post_save
from nxtgenUser.models import NxtgenUser
from studentProfile.models import StudentProfile

class TeacherProfile(models.Model):
	teacher = models.OneToOneField(NxtgenUser, on_delete=models.CASCADE)

	def __str__(self):
		return self.teacher.nxtgen_user.email		

# post save signal
def create_TeacherProfile(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], 'teacher_profile') == True:
			TeacherProfile.objects.create(
				teacher=kwargs['instance']
				)
		else:
			return None

post_save.connect(create_TeacherProfile, sender=NxtgenUser)


class TeacherRegistrationNumber(models.Model):
	teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE)
	institution = models.ForeignKey('institution.Institution', on_delete=models.CASCADE)
	registration_number = models.CharField(max_length=50)

	class Meta:
		unique_together = (("teacher", "institution"), ("institution", "registration_number"))

	def __str__(self):
		return self.teacher.teacher.nxtgen_user.email + " / " + self.institution.name



class TeacherFollowerRelation(models.Model):
	teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE)
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("teacher", "student")

	def __str__(self):
		return self.teacher.teacher.nxtgen_user.email +" / "+ self.student.student.nxtgen_user.email

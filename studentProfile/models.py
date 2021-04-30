from django.db import models
from django.db.models.signals import post_save
from nxtgenUser.models import NxtgenUser
#from institution.models import Institution

# Create your models here.

class StudentProfile(models.Model):
	student = models.OneToOneField(NxtgenUser, on_delete=models.CASCADE)

	def __str__(self):
		return self.student.nxtgen_user.email

# post save signal
def create_StudentProfile(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], 'student_profile') == True:
			StudentProfile.objects.create(
				student=kwargs['instance']
				)
		else:
			return None

post_save.connect(create_StudentProfile, sender=NxtgenUser)



class StudentRegistrationNumber(models.Model):
	student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
	institution = models.ForeignKey('institution.Institution', on_delete=models.CASCADE)
	registration_number = models.CharField(max_length=50)

	class Meta:
		unique_together = (("student", "institution"), ("institution", "registration_number"))

	def __str__(self):
		return self.student.student.nxtgen_user.email + " / " + self.institution.name

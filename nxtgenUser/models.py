from django.db import models
from account.models import User
from django.db.models.signals import post_save


class NxtgenUser(models.Model):
	nxtgen_user = models.OneToOneField(User, on_delete=models.CASCADE)
	student_profile = models.BooleanField(default=False)
	teacher_profile = models.BooleanField(default=False)
	management_profile = models.BooleanField(default=False)

	def __str__(self):
		return self.nxtgen_user.email

#post save signal
def create_NxtgenUser(sender, **kwargs):
	if kwargs['created']:
		nxtgen_user_obj = NxtgenUser(nxtgen_user=kwargs['instance'])

		if hasattr(kwargs['instance'], '_student_profile'):
			nxtgen_user_obj.student_profile=kwargs['instance']._student_profile

		if hasattr(kwargs['instance'], '_teacher_profile'):
			nxtgen_user_obj.teacher_profile=kwargs['instance']._teacher_profile

		nxtgen_user_obj.save()

post_save.connect(create_NxtgenUser, sender=User, weak=False)
from django.db import models
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models.signals import post_save
from utility.obscure_util import obscure
from institution.models import Institution


class UserInvite(models.Model):
	STATUS_CHOICE = (
           ('send','SEND'),
           ('rejected','REJECTED'),
           ('excepted','EXCEPTED'),
		)
	PROFILE_CHOICE = (
           ('stu','STUDENT'),
           ('teach','TEACHER'),
		)

	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
	email = models.EmailField()
	register_number = models.CharField(max_length=50)
	invite_status = models.CharField(max_length=20, choices=STATUS_CHOICE)
	profile_type = models.CharField(max_length=20, choices=PROFILE_CHOICE)
	date = models.DateField(auto_now=True, auto_now_add=False)

	class Meta:
		unique_together = (("institution", "register_number"), ("institution", "email"))

	def __str__(self):
		return self.institution.name +" / "+ self.email +" / "+ self.invite_status

def send_invite_link(sender, **kwargs):
	if kwargs['created']:
		instance = kwargs['instance']
		current_site = Site.objects.get_current().domain

		invite_link = "{0}/invite/{1}".format(
			current_site,obscure(str(instance.id).encode())
			)
		'''
		subject = 'invitation for joining ' + instance.institution.name + 'as a ' + instance.profile_type
		message = "Hello {0},{1}".format(instance.email, invite_link)

		send_mail(subject, message, 'asgerscicity@gmail.com', [instance.email], fail_silently=False)
		'''


post_save.connect(send_invite_link, sender=UserInvite)
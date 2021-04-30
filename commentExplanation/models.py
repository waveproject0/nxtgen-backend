from django.db import models
from django.contrib.postgres.fields import JSONField
from nxtgenUser.models import NxtgenUser


class Comment(models.Model):
	it_self = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
	commenter = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	publish = models.DateTimeField(auto_now_add=True)
	body = models.TextField()
	stared = models.BooleanField(default=False)

	def __str__(self):
		return self.commenter.nxtgen_user.email +" / "+ self.body



class Explanation(models.Model):
	body = JSONField()
	author = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.auther.nxtgen_user.email +" / "+ str(self.created)
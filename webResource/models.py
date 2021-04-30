from django.db import models
from course.models import Subject, SubTopic, Topic
from Class.models import Class
from nxtgenUser.models import NxtgenUser

class WebLink(models.Model):
	link = models.URLField(max_length=500, unique=True)

	def __str__(self):
		return self.link


class ResourceCollection(models.Model):
	title = models.CharField(max_length=50)

	def __str__(self):
		return self.title

class Resource(models.Model):
	web_link = models.ForeignKey('WebLink', on_delete=models.SET_NULL, null=True, blank=True)
	Class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
	sub_topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, null=True, blank=True)
	resource_collection = models.ForeignKey('ResourceCollection', on_delete=models.CASCADE, null=True, blank=True)
	uploader = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return self.Class.id +" / "+ self.uploader.nxtgen_user.email
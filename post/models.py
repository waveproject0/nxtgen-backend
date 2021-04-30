from django.db import models
from django.contrib.postgres.fields import JSONField


class Post(models.Model):
	title = models.CharField(max_length=100)
	data = JSONField()
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

class PostWide(models.Model):
	wide_option = models.CharField(max_length=20)

	def __str__(self):
		return self.wide_option
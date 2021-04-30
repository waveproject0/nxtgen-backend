from django.db import models


class Course(models.Model):
	name = models.CharField(max_length=500)
	innecials = models.CharField(max_length=20)
	version = models.PositiveIntegerField()

	class Meta:
		unique_together = ("name", "version")

	def __str__(self):
		return self.name +" / "+ str(self.version)


class CourseSubjectRelation(models.Model):
	course = models.ForeignKey('Course', on_delete=models.CASCADE)
	subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
	position = models.PositiveIntegerField(null=True, blank=True) 

	class Meta:
		unique_together = ("course", "subject")

	def __str__(self):
		return self.course.name + " / " + self.subject.name


class Subject(models.Model):
	name = models.CharField(max_length=500)
	version = models.PositiveIntegerField()

	class Meta:
		unique_together = ("name", "version")

	def __str__(self):
		return self.name+" / "+ str(self.version)


class SubjectTopicRelation(models.Model):
	subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
	topic = models.ForeignKey('Topic',on_delete=models.CASCADE)
	position = models.PositiveIntegerField(null=True, blank=True)

	class Meta:
		unique_together = ("subject", "topic")

	def __str__(self):
		return self.subject.name +" / "+ self.topic.name


class Topic(models.Model):
	name = models.CharField(max_length=500)
	version = models.PositiveIntegerField()

	class Meta:
		unique_together = ("name", "version")

	def __str__(self):
		return self.name+" / "+ str(self.version)


class TopicSubTopicRelation(models.Model):
	topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
	sub_topic = models.ForeignKey('SubTopic', on_delete=models.CASCADE)
	position = models.PositiveIntegerField(null=True, blank=True)

	class Meta:
		unique_together = ("sub_topic", "topic")

	def __str__(self):
		return self.topic.name +" / "+ self.sub_topic.name


class SubTopic(models.Model):
	name = models.CharField(max_length=500, unique=True)

	def __str__(self):
		return self.name
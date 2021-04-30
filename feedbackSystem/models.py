from django.db import models
from Class.models import ClassStudentSubjectTeacherRelation, ClassSubjectTeacherRelation


class Feedback(models.Model):
	class_subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE)
	feedback_message = models.ForeignKey('FeedbackMessage', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("class_subject_teacher", "feedback_message")

	def __str__(self):
		return self.class_subject_teacher.id +" / "+ self.feedback_message.id


class FeedbackMessage(models.Model):
	message = models.TextField()

	def __str__(self):
		return self.message


class FeedbackSupport(models.Model):
	value = models.BooleanField(default=False)
	feedback = models.ForeignKey('Feedback', on_delete=models.CASCADE)
	student = models.ForeignKey(ClassStudentSubjectTeacherRelation, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("feedback", "student")

	def __str__(self):
		return self.value +" / "+ self.student.id
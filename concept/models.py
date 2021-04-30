from django.db import models
from nxtgenUser.models import NxtgenUser
from course.models import Subject
from commentExplanation.models import Explanation


class Concept(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField()
	edited_version = models.BooleanField(default=False)
	it_self = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.name +" / "+ self.edited_version


class ConceptApprovedEdit(models.Model):
	concept = models.ForeignKey('Concept', on_delete=models.CASCADE)
	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("concept", "user")

	def __str__(self):
		return self.concept.name +" / "+ self.user.nxtgen_user.email


class ConceptExplanation(models.Model):
	concept = models.ForeignKey('Concept', on_delete=models.CASCADE)
	explanation = models.OneToOneField(Explanation, on_delete=models.CASCADE)



class ConceptEdit(models.Model):
	edited_concept = models.ForeignKey('Concept', on_delete=models.CASCADE)
	approved_by = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("edited_concept", "approved_by")

	def __str__(self):
		return self.edited_concept.name +" / "+ self.approved_by.name



class ConceptSubjectRelation(models.Model):
	concept = models.ForeignKey('Concept', on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("subject", "concept")

	def __str__(self):
		return self.concept.name +" / "+ self.subject.name
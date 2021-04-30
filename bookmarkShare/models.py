from django.db import models
from nxtgenUser.models import NxtgenUser
from date.models import PublicDateInstitutionRelation
from form.models import FormPost
from questionBank.models import Question
from Class.models import Class, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation

class AbstractBookmark(models.Model):
	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	saved_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True


class PublicDateBookmark(AbstractBookmark):
	public_date = models.ForeignKey(PublicDateInstitutionRelation, on_delete=models.SET_NULL, null=True)

	class Meta:
		unique_together = ("user", "public_date")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.public_date.date_institution.date.date


class FormPostBookmark(AbstractBookmark):
	form_post = models.ForeignKey(FormPost, on_delete=models.SET_NULL, null=True)

	class Meta:
		unique_together = ("user", "form_post")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.form_post.post.title


class QuestionBookmark(AbstractBookmark):
	question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)

	class Meta:
		unique_together = ("user", "question")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.question.title



#------------------------------------------------------------------------------------------------------

class AbstractShare(models.Model):
	user = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)
	shared_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True

class FormPostShare(AbstractShare):
	SHARED_ON = (
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	form_post = models.ForeignKey(FormPost, on_delete=models.CASCADE)
	shared_on = models.CharField(max_length=20,choices=SHARED_ON)
	shared_on_subject = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE, null=True)
	shared_on_additional_subject = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE, null=True)

	class Meta:
		unique_together = (("form_post","user","shared_on_subject"),("form_post","user","shared_on_additional_subject"))

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.form_post.post.title


class QuestionShare(AbstractShare):
	SHARED_ON = (
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	shared_on = models.CharField(max_length=20,choices=SHARED_ON)
	shared_on_subject = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE, null=True)
	shared_on_additional_subject = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE, null=True)

	class Meta:
		unique_together = (("question","user","shared_on_subject"),("question","user","shared_on_additional_subject"))

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.question.title
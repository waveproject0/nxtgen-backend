from django.db import models
from nxtgenUser.models import NxtgenUser
from form.models import FormPost, TopicFormQuery, SubTopicFormQuery
from commentExplanation.models import Explanation
from date.models import PublicDateInstitutionRelation
from questionBank.models import Question


class AbstractPoll(models.Model):
	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	saved_at = models.DateTimeField(auto_now=True)
	value = models.BooleanField()

	class Meta:
		abstract = True


class LikeFormPost(AbstractPoll):
	form_post = models.ForeignKey(FormPost, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "form_post")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.value +" / "+ self.form_post.post.title

class LikePublicDate(AbstractPoll):
	public_date = models.ForeignKey(PublicDateInstitutionRelation, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "public_date")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.value +" / "+ str(self.public_date.date_institution.date.date)


class LikeQuestion(AbstractPoll):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "question")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.value +" / "+ self.question.body.title



class QuestionIsCorrect(AbstractPoll):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "question")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.value +" / "+ self.question.body.title


class VoteExplanation(AbstractPoll):
	explanation = models.ForeignKey(Explanation, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "explanation")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.value


class AbstractRelevance(models.Model):
	RELEVANT_OPTION = (
			('irrelevant','Irrelevant'),
			('relevant','Relevant'),
			('highly relevant','Highly-Relevant')
		)

	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	saved_at = models.DateTimeField(auto_now=True)
	relevance = models.CharField(max_length=30,choices=RELEVANT_OPTION)

	class Meta:
		abstract = True


class RelevantTopicFormQuery(AbstractRelevance):
	form_query = models.ForeignKey(TopicFormQuery, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "form_query")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.relevance +" / "+ self.form_query.post.title


class RelevantSubTopicFormQuery(AbstractRelevance):
	form_query = models.ForeignKey(SubTopicFormQuery, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "form_query")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.relevance +" / "+ self.form_query.post.title



class QuestionDifficulty(models.Model):
	DIFFICULTY_OPTION = (
			('easy','Easy'),
			('medium','Medium'),
			('hard','hard'),
			('challenge','Challenge')
		)

	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	saved_at = models.DateTimeField(auto_now=True)
	difficulty_option = models.CharField(max_length=30,choices=DIFFICULTY_OPTION)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("user", "question")

	def __str__(self):
		return self.user.nxtgen_user.email +" / "+ self.question.body.title
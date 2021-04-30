from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from nxtgenUser.models import NxtgenUser
from Class.models import ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from concept.models import Concept
from exam.models import Exam
from course.models import Course, Subject, Topic, SubTopic
from commentExplanation.models import Explanation

class Question(models.Model):
	QUESTION_TYPE = (
			('accedemic','accedemic'),
			('competative','competative'),
			('research','research'),
			('high order thinking','High order thinking')
		)

	SUBJECT_TYPE = (
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	STATUS_CHOICE = (
			('draft','Draft'),
			('active','Active')
		)

	QUESTION_IN = (
			('subject','Subject'),
			('topic','Topic'),
			('subTopic','SubTopic')
		)


	subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	additional_subject_teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	subject_type = models.CharField(max_length=20,choices=SUBJECT_TYPE, null=True, blank=True)

	title = models.CharField(max_length=200, null=True, blank=True)
	body = JSONField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='draft')
	question_type = models.CharField(max_length=20, choices=QUESTION_TYPE)
	question_in = models.CharField(max_length=20, choices=QUESTION_IN)
	author = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	publish = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	tags = TaggableManager()

	def __str__(self):
		return self.title


class QuestionExplanation(models.Model):
	STATUS_CHOICE = (
			('draft','Draft'),
			('active','Active'),
		)

	question = models.ForeignKey('Question',on_delete=models.CASCADE)
	explanation = models.OneToOneField(Explanation,on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='draft')
	publish = models.DateTimeField(auto_now=False, auto_now_add=False ,null=True, blank=True)

	def __str__(self):
		return self.question.title +" / "+ self.explanation.id


def create_question_explanation(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'],'_explanation_for') == 'question':
			question_explanation_obj = QuestionExplanation(
				question=kwargs['instance']._explanation_for_model_obj,explanation=kwargs['instance']
				)

			if hasattr(kwargs['instance'],'_status'):
				if getattr(kwargs['instance'],'_status') == 'active':
					question_explanation_obj.status = kwargs['instance'],_status
					question_explanation_obj.publish = timezone.now()

			question_explanation_obj.save()


post_save.connect(create_question_explanation, sender=Question, weak=False)



class QuestionConcept(models.Model):
	question = models.ForeignKey('Question',on_delete=models.CASCADE)
	concept = models.ForeignKey(Concept,on_delete=models.CASCADE)

	class Meta:
		unique_together = ("question", "concept")

	def __str__(self):
		return self.question.title +" / "+ self.concept.name


class QuestionExam(models.Model):
	question = models.ForeignKey('Question',on_delete=models.CASCADE)
	exam = models.ForeignKey(Exam,on_delete=models.CASCADE)

	class Meta:
		unique_together = ("question", "exam")

	def __str__(self):
		return self.question.title +" / "+ self.exam.name





class QuestionSubjectRelation(models.Model):
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	question = models.OneToOneField('Question', on_delete=models.CASCADE)

	def __str__(self):
		return self.question.title +" / "+ self.subject.name


class QuestionTopicRelation(models.Model):
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	question = models.OneToOneField('Question', on_delete=models.CASCADE)


	def __str__(self):
		return self.question.title +" / "+ self.topic.name


class QuestionSubtopicRelation(models.Model):
	sub_topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE)
	question = models.OneToOneField('Question', on_delete=models.CASCADE)

	def __str__(self):
		return self.question.title +" / "+ self.sub_topic.name



def create_question_relation(sender, **kwargs):
	if kwargs['created']:
		if hasattr(kwargs['instance'], '_question_relation_name'):
			if getattr(kwargs['instance'], '_question_relation_name') == 'qs_subject':
				QuestionSubjectRelation.objects.create(
					question=kwargs['instance'], subject=kwargs['instance']._course_relation_obj
					)

			if getattr(kwargs['instance'], '_question_relation_name') == 'qs_topic':
				QuestionTopicRelation.objects.create(
					question=kwargs['instance'], topic=kwargs['instance']._course_relation_obj
					)

			if getattr(kwargs['instance'], '_question_relation_name') == 'qs_sub_topic':
				QuestionSubtopicRelation.objects.create(
					question=kwargs['instance'], sub_topic=kwargs['instance']._course_relation_obj
					)



post_save.connect(create_question_relation, sender=Question, weak=False)
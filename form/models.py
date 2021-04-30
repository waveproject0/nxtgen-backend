from django.utils import timezone
from django.db import models
from nxtgenUser.models import NxtgenUser
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from post.models import Post
from institution.models import InstitutionStudentRelation
from Class.models import Class, ClassStudentRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from course.models import Subject, SubjectTopicRelation, TopicSubTopicRelation
from commentExplanation.models import Comment, Explanation


class Form(models.Model):
	Class = models.OneToOneField(Class, on_delete=models.CASCADE)

	def __str__(self):
		return self.Class.course.name +" / "+ self.Class.institution.name

# form create signal
def create_form(sender, **kwargs):
	if kwargs['created']:
		Form.objects.create(Class=kwargs['instance'])

post_save.connect(create_form, sender=Class, weak=False)
# signal ends


class FormPost(models.Model):
	STATUS_CHOICE = (
			('active','Active'),
			('archive','Archived'),
		)

	POST_TYPE = (
			('class','Class only'),
			('educational','Educational'),
			('informational','Informational'),
			('news','News')
		)

	SUBJECT_TYPE = (
			('subject','Subject'),
			('additional subject','Additional subject')
		)
	
	form = models.ForeignKey('Form', on_delete=models.SET_NULL, null=True)
	subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	additional_subject_teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	post = models.OneToOneField(Post, on_delete=models.CASCADE)
	status = models.CharField(max_length=20,choices=STATUS_CHOICE, default='active')
	post_type = models.CharField(max_length=20,choices=POST_TYPE, default='class')
	subject_type = models.CharField(max_length=20,choices=SUBJECT_TYPE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	block_comment = models.BooleanField(default=False)
	author = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)
	public = models.BooleanField(default=False)
	publish = models.DateTimeField(auto_now=False, auto_now_add=True)
	archive_date = models.DateField(auto_now=False, auto_now_add=False)
	tags = TaggableManager()

	def __str__(self):
		return self.subject.name +" / "+ self.post.title +" / "+ self.subject_type


def create_form_post(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'form_post':
			form_post_obj = FormPost(
				form=kwargs['instance']._form_obj, post=kwargs['instance'], subject=kwargs['instance']._subject_obj,
				author=kwargs['instance']._author
				)
			if hasattr(kwargs['instance'], '_block_comment'):
				form_post_obj.block_comment = kwargs['instance']._block_comment

			if hasattr(kwargs['instance'], '_post_type'):
				if kwargs['instance']._post_type != 'class':
					if hasattr(kwargs['instance'], '_public'):
						form_obj.public = kwargs['instance']._public

					form_post_obj.post_type = kwargs['instance']._post_type

			if kwargs['instance']._authority == 'sectionSubjectTeacher' or kwargs['instance']._authority == 'sectionStudentSubjectTeacher':
				form_post_obj.subject_type = 'subject'
				form_post_obj.subject_teacher = kwargs['instance']._section_subject_obj

			if kwargs['instance']._authority == 'sectionAdditionalSubjectTeacher' or kwargs['instance']._authority == 'sectionStudentAdditionalSubjectTeacher':
				form_post_obj.subject_type = 'additional subject'
				form_post_obj.additional_subject_teacher = kwargs['instance']._section_subject_obj

			form_post_obj.archive_date = date.today() + timedelta(days=90)

			form_post_obj.save()

			if hasattr(kwargs['instance'], '_tags'):
				if len(kwargs['instance']._tags) != 0:
					for tag in kwargs['instance']._tags:
						form_post_obj.tags.add(tag)


post_save.connect(create_form_post, sender=Post, weak=False)





class AbstractFormQuery(models.Model):
	STATUS_CHOICE = (
			('active','Active'),
			('archive','Archived'),
		)

	SUBJECT_TYPE = (
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	form = models.ForeignKey('Form', on_delete=models.CASCADE)
	subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE)
	additional_subject_teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE)
	post = models.OneToOneField(Post, on_delete=models.CASCADE)
	status = models.CharField(max_length=20,choices=STATUS_CHOICE, default='active')
	subject_type = models.CharField(max_length=20,choices=SUBJECT_TYPE)
	author = models.ForeignKey(ClassStudentRelation, on_delete=models.SET_NULL, null=True)
	publish = models.DateTimeField(auto_now=False, auto_now_add=True)
	archive_date = models.DateField(auto_now=False, auto_now_add=False)
	tags = TaggableManager()

	class Meta:
		abstract = True


class TopicFormQuery(AbstractFormQuery):
	topic = models.ForeignKey(SubjectTopicRelation, on_delete=models.CASCADE)


	def __str__(self):
		return self.topic.topic.name +" / "+ self.post.title +" / "+ self.subject_type


class SubTopicFormQuery(AbstractFormQuery):
	sub_topic = models.ForeignKey(TopicSubTopicRelation, on_delete=models.CASCADE)


	def __str__(self):
		return self.topic.topic.name +" / "+ self.post.title +" / "+ self.subject_type


def create_form_query(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'topic_form_query' or getattr(kwargs['instance'], '_post_for') == 'sub-topic_form_query':

			if getattr(kwargs['instance'], '_post_for') == 'topic_form_query':
				form_query_obj = TopicFormQuery(topic=kwargs['instance']._subject_topic_obj)

			if getattr(kwargs['instance'], '_post_for') == 'sub-topic_form_query':
				form_query_obj = SubTopicFormQuery(sub_topic=kwargs['instance']._topic_subtopic_obj)

			form_query_obj.form = kwargs['instance']._form_obj
			form_query_obj.subject_type = kwargs['instance']._subject_type
			form_query_obj.author = kwargs['instance']._author

			if getattr(kwargs['instance'], '_subject_type') == 'subject':
				form_query_obj.subject_teacher = kwargs['instance']._subject_teacher_obj

			if getattr(kwargs['instance'], '_subject_type') == 'additional subjct':
				form_query_obj.additional_subject_teacher = kwargs['instance']._additional_subject_teacher_obj

			form_query_obj.archive_date = date.today() + timedelta(days=90)

			form_query_obj.save()

			if hasattr(kwargs['instance'], '_tags'):
				if len(kwargs['instance']._tags) != 0:
					for tag in kwargs['instance']._tags:
						form_query_obj.tags.add(tag)

post_save.connect(create_form_query, sender=Post, weak=False)



class CommentFormPostRelation(models.Model):
	comment = models.OneToOneField(Comment, on_delete=models.CASCADE)
	form_post = models.ForeignKey('FormPost', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.form_post.post.title


class CommentTopicFormQueryRelation(models.Model):
	comment = models.OneToOneField(Comment, on_delete=models.CASCADE)
	topic_form_post = models.ForeignKey('TopicFormQuery', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.topic_form_post.post.title



class CommentSubTopicFormQueryRelation(models.Model):
	comment = models.OneToOneField(Comment, on_delete=models.CASCADE)
	subTopic_form_post = models.ForeignKey('SubTopicFormQuery', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.subTopic_form_post.post.title


def create_comment_form(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'form':
			if getattr(kwargs['instance'], '_form_relation_name') == 'form_post':
				CommentFormPostRelation.objects.create(
					comment=kwargs['instance'],form_post=kwargs['instance']._form_relation_obj
					)

			if getattr(kwargs['instance'], '_form_relation_name') == 'topic_form_query':
				CommentTopicFormQueryRelation.objects.create(
					comment=kwargs['instance'],topic_form_post=kwargs['instance']._form_relation_obj
					)

			if getattr(kwargs['instance'], '_form_relation_name') == 'subTopic_form_query':
				CommentSubTopicFormQueryRelation.objects.create(
					comment=kwargs['instance'],subTopic_form_post=kwargs['instance']._form_relation_obj
					)


post_save.connect(create_comment_form, sender=Comment, weak=False)



class AbstractFormQueryExplanation(models.Model):
	STATUS_CHOICE = (
			('draft','Draft'),
			('active','Active'),
			('archive','Archived'),
		)
	explanation = models.OneToOneField(Explanation, on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='draft')
	publish = models.DateTimeField(auto_now=False, auto_now_add=False ,null=True, blank=True)

	class Meta:
		abstract = True


class ExplanationTopicFormQueryRelation(AbstractFormQueryExplanation):
	topic_form_post = models.ForeignKey('TopicFormQuery', on_delete=models.CASCADE)

	def __str__(self):
		return self.explanation.author.nxtgen_user.email +" / "+ self.topic_form_post.post.title



class ExplanationSubTopicFormQueryRelation(AbstractFormQueryExplanation):
	subTopic_form_post = models.ForeignKey('SubTopicFormQuery', on_delete=models.CASCADE)

	def __str__(self):
		return self.explanation.author.nxtgen_user.email +" / "+ self.subTopic_form_post.post.title



def create_explanation_form_query(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_explanation_for') in ('explanation_topic_form_query','explanation_sub-topic_form_query'):
			if getattr(kwargs['instance'],'_explanation_for') == 'explanation_topic_form_query':
				explanation_form_query_obj = ExplanationTopicFormQueryRelation(
					explanation=kwargs['instance'],topic_form_post=kwargs['instance']._explanation_for_model_obj
					)

			if getattr(kwargs['instance'],'_explanation_for') == 'explanation_sub-topic_form_query':
				explanation_form_query_obj = ExplanationSubTopicFormQueryRelation(
					explanation=kwargs['instance'],subTopic_form_post=kwargs['instance']._explanation_for_model_obj
					)

			if hasattr(kwargs['instance'],'_status'):
				if getattr(kwargs['instance'],'_status') == 'active':
					explanation_form_query_obj.status = 'active'
					explanation_form_query_obj.publish = timezone.now()

			explanation_form_query_obj.save()

post_save.connect(create_explanation_form_query, sender=Explanation, weak=False)





class AbstractImproveRequest(models.Model):
	message = models.CharField(max_length=500)
	requester = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	publish = models.DateTimeField(auto_now=False, auto_now_add=True)

	class Meta:
		abstract = True


class TopicQueryImproveRequest(AbstractImproveRequest):
	form_query = models.ForeignKey('TopicFormQuery', on_delete=models.CASCADE)


	def __str__(self):
		return self.form_query.post.title +" / "+ self.requester.nxtgen_user.email


class SubTopicQueryImproveRequest(AbstractImproveRequest):
	form_query = models.ForeignKey('SubTopicFormQuery', on_delete=models.CASCADE)


	def __str__(self):
		return self.form_query.post.title +" / "+ self.requester.nxtgen_user.email


class TopicExplanationImproveRequest(AbstractImproveRequest):
	form_explanation = models.ForeignKey('ExplanationTopicFormQueryRelation', on_delete=models.CASCADE)


	def __str__(self):
		return self.form_explanation.topic_form_post.post.title +" / "+ self.requester.nxtgen_user.email


class SubTopicExplanationImproveRequest(AbstractImproveRequest):
	form_explanation = models.ForeignKey('ExplanationSubTopicFormQueryRelation', on_delete=models.CASCADE)


	def __str__(self):
		return self.form_explanation.subTopic_form_post.post.title +" / "+ self.requester.nxtgen_user.email
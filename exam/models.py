from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from taggit.managers import TaggableManager
from post.models import Post
from Class.models import ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation, ClassStudentSubjectTeacherRelation,\
ClassStudentAdditionalSubjectTeacherRelation
from commentExplanation.models import Comment, Explanation
#from questionBank.models import Question, QuestionExplanation
from nxtgenUser.models import NxtgenUser



class Exam(models.Model):
	EXAM_LEVEL = (
		 ('primary','primary'),
		 ('high','High'),
		 ('higher secondery','Higher secondery'),
		 ('ug','UG'),
		 ('pg','PG'),
		 ('phd','PHD'),
		 ('research','Research')
		)

	EXAM_TYPE = (
			('academic','Academic'),
			('compitative', 'compitative'),
			('entrance','Entrance'),
			('job selection','Job selection')
		)

	EXAM_SPREAD = (
			('local','Local'),
			('national','Nationl'),
			('international','International')
		)

	name = models.CharField(max_length=50, unique=True)
	acroname = models.CharField(max_length=10)
	exam_level = models.CharField(max_length=20, choices=EXAM_LEVEL)
	exam_type = models.CharField(max_length=20, choices=EXAM_TYPE)
	exam_spread = models.CharField(max_length=20, choices=EXAM_SPREAD)
	description = models.CharField(max_length=500, null=True, blank=True)
	official_link = models.URLField(max_length=500, unique=True, null=True, blank=True)

	def __str__(self):
		return self.acroname


class ExamApprovedEdit(models.Model):
	exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
	user = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("exam", "user")

	def __str__(self):
		return self.exam.acroname +" / "+ self.user.nxtgen_user.email



class ExamPost(models.Model):
	exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
	post = models.OneToOneField(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	publish = models.DateTimeField(auto_now_add=True)
	block_comment = models.BooleanField(default=False)
	tags = TaggableManager()

	class Meta:
		unique_together = ("exam", "post")

	def __str__(self):
		return self.exam.acroname +" / "+ self.post.title


class ExamQuery(models.Model):
	exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
	query = models.OneToOneField(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)
	publish = models.DateTimeField(auto_now_add=True)
	block_comment = models.BooleanField(default=False)
	tags = TaggableManager()

	class Meta:
		unique_together = ("exam", "query")

	def __str__(self):
		return self.exam.acroname +" / "+ self.post.title



def create_exam_content(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') in ('exam_post','exam_query'):
			if getattr(kwargs['instance'], '_post_for') == 'exam_post':
				exam_content_obj = ExamPost(post=kwargs['instance'])

			if getattr(kwargs['instance'], '_post_for') == 'exam_query':
				exam_content_obj = ExamQuery(query=kwargs['instance'])

			exam_content_obj.exam = kwargs['instance']._exam_obj
			exam_content_obj.author = kwargs['instance']._author

			if hasattr(kwargs['instance'], '_block_comment'):
				exam_content_obj.block_comment = kwargs['instance']._block_comment

			exam_content_obj.save()

			if hasattr(kwargs['instance'], '_tags'):
				if len(kwargs['instance']._tags) != 0:
					for tag in kwargs['instance']._tags:
						exam_content_obj.tags.add(tag)


post_save.connect(create_exam_content, sender=Post, weak=False)



class ExamQueryExplanation(models.Model):
	STATUS_TYPE = (
			('draft','Draft'),
			('active','Active')
		)

	exam_query = models.ForeignKey('ExamQuery', on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=STATUS_TYPE, default='draft')
	explanation = models.OneToOneField(Explanation, on_delete=models.CASCADE)
	publish = models.DateTimeField(auto_now_add=True, null=True, blank=True)

	def __str__(self):
		return self.exam_query.post.title +" / "+ self.explanation


def create_exam_query_explanation(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_explanation_for') == 'exam_query':
			exam_query_explanation_obj = ExamQueryExplanation(
				exam_query=kwargs['instance']._explanation_for_model_obj,explanation=kwargs['instance']
				)
			if hasattr(kwargs['instance'], '_status'):
				if getattr(kwargs['instance'], '_status') == 'active':
					exam_query_explanation_obj.status = 'active'
					exam_query_explanation_obj.publish = timezone.now()

			exam_query_explanation_obj.save()


post_save.connect(create_exam_query_explanation, sender=Explanation, weak=False)


class AbstractExamComment(models.Model):
	comment = models.OneToOneField(Comment, on_delete=models.CASCADE)

	class Meta:
		abstract = True



class ExamPostComment(AbstractExamComment):
	exam_post = models.ForeignKey('ExamPost',on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.exam_post.post.title



class ExamQueryComment(AbstractExamComment):
	exam_query = models.ForeignKey('ExamQuery',on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.exam_query.post.title



class ExamQueryExplanationComment(AbstractExamComment):
	exam_query_explanation = models.ForeignKey('ExamQueryExplanation', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.exam_query_explanation.explanation.id


class TestComment(AbstractExamComment):
	test = models.ForeignKey('Test', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.test_posting.title


def create_exam_comment(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'exam':
			if getattr(kwargs['instance'], '_comment_on') == 'exam_post':
				exam_comment_obj = ExamPostComment(exam_post=kwargs['instance']._comment_on_obj)

			if getattr(kwargs['instance'], '_comment_on') == 'exam_query':
				exam_comment_obj = ExamQueryComment(exam_query=kwargs['instance']._comment_on_obj)

			if getattr(kwargs['instance'], '_comment_on') == 'exam_query_explanation':
				exam_comment_obj = ExamQueryExplanationComment(exam_query_explanation=kwargs['instance']._comment_on_obj)

			if getattr(kwargs['instance'], '_comment_on') == 'test':
				exam_comment_obj = TestComment(test=kwargs['instance']._comment_on_obj)

			exam_comment_obj.comment = kwargs['instance']
			exam_comment_obj.save()


post_save.connect(create_exam_comment, sender=Comment, weak=False)



class Test(models.Model):
	STATUS_CHOICE = (
			('draft','Draft'),
			('active','Active'),
			('archive','Archived')
		)

	CLASS_SUBJECT_TYPE = (
			('none','None'),
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	TEST_TYPE = (
			('subjective','Subjective'),
			('objective','Objective')
		)
	exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
	title = models.CharField(max_length=200, null=True, blank=True)
	subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	additional_subject_teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='draft')
	class_subject_type = models.CharField(max_length=20, choices=CLASS_SUBJECT_TYPE)
	test_type = models.CharField(max_length=20, choices=TEST_TYPE)
	marking = models.BooleanField(default=False)
	negative_marking = models.BooleanField(default=False)
	author = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)
	public = models.BooleanField(default=True)
	publish = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
	tags = TaggableManager()

	def __str__(self):
		return self.title +" / "+ self.test_type

def adding_tags(sender, **kwargs):
	if kwargs['created']:
		if hasattr(kwargs['instance'], '_tags'):
			kwargs['instance'].tags.clear()
			if len(kwargs['instance']._tags) != 0:
				for tag in kwargs['instance']._tags:
					kwargs['instance'].tags.add(tag)

post_save.connect(adding_tags, sender=Test, weak=False)




class TestSection(models.Model):
	test = models.ForeignKey('Test', on_delete=models.CASCADE)
	section = models.CharField(max_length=100)
	position = models.PositiveIntegerField()

	def __str__(self):
		return self.section

def create_test_section(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_question_arrangement') == 'test_section':
			for section in kwargs['instance']._test_sections:
				test_section_obj = TestSection(
					test=kwargs['instance'],section=section['section_name'],position=section['position']
					)
				test_section_obj._section_questions = section['test_question']
				test_section_obj.save()


post_save.connect(create_test_section, sender=Test, weak=False)

class TestQuestion(models.Model):
	test = models.ForeignKey('Test', on_delete=models.CASCADE)
	question = models.ForeignKey('questionBank.Question', on_delete=models.CASCADE)
	explanation = models.ForeignKey('questionBank.QuestionExplanation', on_delete=models.SET_NULL, null=True)
	ans_choices = models.BooleanField(default=False)
	section = models.ForeignKey('TestSection', null=True, blank=True, on_delete=models.CASCADE)
	positive_marks = models.PositiveIntegerField(null=True, blank=True)
	negative_marks = models.PositiveIntegerField(null=True, blank=True)
	position = models.PositiveIntegerField()
	
	class Meta:
		unique_together = ("test", "question", "position")

	def __str__(self):
		return self.test.title +" / "+ self.question.title

def create_section_question(sender, **kwargs):
	if kwargs['created']:
		if hasattr(kwargs['instance'], '_section_questions'):

			for question in kwargs['instance']._section_questions:
				test_question_obj = TestQuestion(
					test=kwargs['instance'].test,section=kwargs['instance'],position=question['position'],
					question=question['question_obj'],explanation=question['question_explanation_obj']
					)

				if 'positive_marks' in question:
					test_question_obj.positive_marks = question['positive_marks']

				if 'negative_marks' in question:
					test_question_obj.negative_marks = question['negative_marks']

				test_question_obj.save()

post_save.connect(create_section_question, sender=TestSection, weak=False)


def create_test_question(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_question_arrangement') == 'test_question':
			for question in kwargs['instance']._test_questions:
				test_question_obj = TestQuestion(
					test=kwargs['instance'],question=question['question_obj'],explanation=question['question_explanation_obj'],
					position=question['position']
					)

				if 'positive_marks' in question:
					test_question_obj.positive_marks = question['positive_marks']

				if 'negative_marks' in question:
					test_question_obj.negative_marks = question['negative_marks']

				test_question_obj.save()

post_save.connect(create_test_question, sender=Test, weak=False)




class TestQuestionChoice(models.Model):
	test_question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
	choice = models.CharField(max_length=500)
	correct = models.BooleanField(default=False)

	class Meta:
		unique_together = ("test_question", "choice")

	def __str__(self):
		return self.test_question.question.title +" / "+ self.choice +" / "+ self.correct_choice

def create_question_choices(sender, **kwargs):
	if kwargs['created']:
		if hasattr(kwargs['instance'], '_question_choices'):
			for choice in kwargs['instance']._question_choices:
				question_choice_obj = TestQuestionChoice(
					test_question=kwargs['instance'],choice=choice['choice']
					)

				if 'correct' in choice:
					question_choice_obj.correct = choice['correct']

				question_choice_obj.save()


post_save.connect(create_question_choices, sender=TestQuestion, weak=False)






class TestStudent(models.Model):
	STUDENT_TYPE = (
			('none','None'),
			('subject','Subject'),
			('additional subject','Additional subject')
		)

	test = models.ForeignKey('Test', on_delete=models.CASCADE)
	subject_student = models.ForeignKey(ClassStudentSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	additional_subject_student = models.ForeignKey(ClassStudentAdditionalSubjectTeacherRelation, on_delete=models.SET_NULL, null=True)
	student_type = models.CharField(max_length=20, choices=STUDENT_TYPE)
	student = models.ForeignKey(NxtgenUser, on_delete=models.SET_NULL, null=True)

	class Meta:
		unique_together = ("test", "student")

	def __str__(self):
		return test.title +" / "+ self.student.nxtgen_user.email


class TestStudentAttempt(models.Model):
	test_student = models.ForeignKey('TestStudent', on_delete=models.SET_NULL, null=True)
	duration_in_minute = models.DurationField()
	total_marks = models.IntegerField(null=True, blank=True)
	completed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("test_student", "date")

	def __str__(self):
		return self.test_student.student.nxtgen_user.email +" / "+ self.date



class TestQuestionStudentChoice(models.Model):
	question_choice = models.ForeignKey('TestQuestionChoice', on_delete=models.CASCADE)
	attempted_student = models.ForeignKey('TestStudentAttempt', on_delete=models.CASCADE)

	class Meta:
		unique_together = ("question_choice", "attempted_student")

	def __str__(self):
		return self.attempted_student.test_student.student.nxtgen_user.email +" / "+ self.question_choice.choice


class TestQuestionStudentExplanation(models.Model):
	attempted_student = models.ForeignKey('TestStudentAttempt', on_delete=models.CASCADE)
	question = models.ForeignKey('TestQuestion',on_delete=models.CASCADE)
	explanation = JSONField()

	class Meta:
		unique_together = ("attempted_student", "question")

	def __str__(self):
		return self.attempted_student.test_student.student.nxtgen_user.email +" / "+ self.question.id






class ExamFollowerRelation(models.Model):
	exam = models.ForeignKey('Exam', on_delete=models.CASCADE)
	follower = models.ForeignKey(NxtgenUser, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("exam", "follower")

	def __str__(self):
		return self.exam.acroname +" / "+ self.follower.nxtgen_user.email
import json
from datetime import timedelta
from django.utils import timezone
from django.forms import URLField
from django.core.exceptions import ValidationError
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest


from .models import Exam, ExamFollowerRelation, ExamApprovedEdit, ExamPost, ExamQuery, ExamQueryExplanation, ExamPostComment,\
ExamQueryComment, ExamQueryExplanationComment, TestComment, Test, TestSection, TestQuestion, TestQuestionChoice,\
TestStudent, TestStudentAttempt, TestQuestionStudentChoice, TestQuestionStudentExplanation

from commentExplanation.models import Comment
from Class.models import ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation, ClassStudentSubjectTeacherRelation,\
ClassStudentAdditionalSubjectTeacherRelation
from questionBank.models import Question, QuestionExplanation


class ExamNode(DjangoObjectType):
    class Meta:
        model = Exam
        filter_fields = []
        interfaces = (relay.Node, )


class ExamFollowerRelationNode(DjangoObjectType):
    class Meta:
        model = ExamFollowerRelation
        filter_fields = []
        interfaces = (relay.Node, )


class ExamPostNode(DjangoObjectType):
    class Meta:
        model = ExamPost
        filter_fields = []
        interfaces = (relay.Node, )


class ExamQueryNode(DjangoObjectType):
    class Meta:
        model = ExamQuery
        filter_fields = []
        interfaces = (relay.Node, )


class ExamQueryExplanationNode(DjangoObjectType):
    class Meta:
        model = ExamQueryExplanation
        filter_fields = []
        interfaces = (relay.Node, )


class ExamPostCommentNode(DjangoObjectType):
    class Meta:
        model = ExamPostComment
        filter_fields = []
        interfaces = (relay.Node, )


class ExamQueryCommentNode(DjangoObjectType):
    class Meta:
        model = ExamQueryComment
        filter_fields = []
        interfaces = (relay.Node, )


class ExamQueryExplanationCommentNode(DjangoObjectType):
    class Meta:
        model = ExamQueryExplanationComment
        filter_fields = []
        interfaces = (relay.Node, )


class TestCommentNode(DjangoObjectType):
    class Meta:
        model = TestComment
        filter_fields = []
        interfaces = (relay.Node, )


class TestNode(DjangoObjectType):
    class Meta:
        model = Test
        filter_fields = []
        interfaces = (relay.Node, )


class TestSectionNode(DjangoObjectType):
    class Meta:
        model = TestSection
        filter_fields = []
        interfaces = (relay.Node, )


class TestQuestionNode(DjangoObjectType):
    class Meta:
        model = TestQuestion
        filter_fields = []
        interfaces = (relay.Node, )


class TestQuestionChoiceNode(DjangoObjectType):
    class Meta:
        model = TestQuestionChoice
        filter_fields = []
        interfaces = (relay.Node, )


class TestStudentNode(DjangoObjectType):
    class Meta:
        model = TestStudent
        filter_fields = []
        interfaces = (relay.Node, )


class TestStudentAttemptNode(DjangoObjectType):
    class Meta:
        model = TestStudentAttempt
        filter_fields = []
        interfaces = (relay.Node, )


class TestQuestionStudentChoiceNode(DjangoObjectType):
    class Meta:
        model = TestQuestionStudentChoice
        filter_fields = []
        interfaces = (relay.Node, )


class TestQuestionStudentExplanationNode(DjangoObjectType):
    class Meta:
        model = TestQuestionStudentExplanation
        filter_fields = []
        interfaces = (relay.Node, )








class Query(graphene.ObjectType):
	exam = relay.Node.Field(ExamNode)
	all_exam = DjangoFilterConnectionField(ExamNode)

	exam_post = relay.Node.Field(ExamPostNode)
	all_exam_post = DjangoFilterConnectionField(ExamPostNode)

	exam_query = relay.Node.Field(ExamQueryNode)
	all_exam_query = DjangoFilterConnectionField(ExamQueryNode)

	test = relay.Node.Field(TestNode)
	all_test = DjangoFilterConnectionField(TestNode)







class ExamMutation(relay.ClientIDMutation):
	exam = graphene.Field(ExamNode)

	class Input:
		name = graphene.String()
		acroname = graphene.String()
		description = graphene.String()
		official_link = graphene.String()
		exam_level = graphene.String()
		exam_type = graphene.String()
		exam_spread = graphene.String()
		exam_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2):
			raise GraphQLError('provide proper value')

		if info.context.user.is_authenticated and info.context.user.is_active:
			if input.get('mutation_option') == 1:

				if input.get('name') is None or input.get('acroname') is None or input.get('exam_level') is None or\
					input.get('exam_type'):
					raise GraphQLError('provide complete information')

				if Exam.objects.filter(name=input.get('name')).exists():
					raise GraphQLError('exam already exists with this name')

				disc = (
						(input.get('exam_level'), Exam.EXAM_LEVEL),
						(input.get('exam_type'), Exam.EXAM_TYPE),
						(input.get('exam_spread'), Exam.EXAM_SPREAD)
					)

				for dis in disc:
					valide_choice = False

					for choice in dis[1]:
						if dis[0] == choice[0]:
							valide_choice = True
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')

				exam_obj = Exam(
					name=input.get('name'),acroname=input.get('acroname'),
					exam_level=input.get('exam_level'),exam_type=input.get('exam_type'),exam_spread=input.get('exam_spread')
					)

				if input.get('description') is not None:
					exam_obj.description = input.get('description')

				if input.get('official_link') is not None:
					url_check = URLField()
					try:
						url_check.clean(input.get('official_link'))
					except ValidationError:
						raise GraphQLError('provide valide URL.')

					exam_obj.official_link = input.get('official_link')

				exam_obj.save()

				return ExamMutation(exam=exam_obj)


			if input.get('mutation_option') == 2:
				if input.get('exam_id') is None:
					raise GraphQLError('provide complete information')

				try:
					exam_obj = Exam.objects.get(id=from_global_id(input.get('exam_id'))[1])
				except Exam.DoesNotExist:
					raise GraphQLError('exam ID is incorrect')

				if ExamApprovedEdit.objects.filter(exam=exam_obj,user=info.context.user.nxtgenuser).exists() is not True:
					raise GraphQLError('you are not approvided to apply any changes to this exam')

				if input.get('name') is not None:
					exam_obj.name = input.get('name')

				if input.get('acroname') is not None:
					exam_obj.acroname = input.get('acroname')

				if input.get('description') is not None:
					exam_obj.description = input.get('description')

				if input.get('official_link') is not None:
					url_check = URLField()
					try:
						url_check.clean(input.get('official_link'))
					except ValidationError:
						raise GraphQLError('provide valide URL.')

					exam_obj.official_link = input.get('official_link')

				if input.get('exam_level') is not None:
					valide_choice = False

					for choice in Exam.EXAM_LEVEL:
						if input.get('exam_level') == choice[0]:
							valide_choice = True
							exam_obj.exam_level = input.get('exam_level')
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')


				if input.get('exam_type') is not None:
					valide_choice = False

					for choice in Exam.EXAM_TYPE:
						if input.get('exam_type') == choice[0]:
							valide_choice = True
							exam_obj.exam_type = input.get('exam_type')
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')


				if input.get('exam_spread') is not None:
					valide_choice = False

					for choice in Exam.EXAM_SPREAD:
						if input.get('exam_spread') == choice[0]:
							valide_choice = True
							exam_obj.exam_spread = input.get('exam_spread')
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')


				exam_obj.save()

				return ExamMutation(exam=exam_obj)


class ExamFollowMutation(relay.ClientIDMutation):
	exam_follower = graphene.Field(ExamFollowerRelationNode)

	class Input:
		exam_id = graphene.ID()
		exam_follower_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		if info.context.user.is_authenticated and info.context.user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('exam_id') is None:
					raise GraphQLError('provide complete information')

				try:
					exam_obj = Exam.objects.get(id=from_global_id(input.get('exam_id'))[1])
				except Exam.DoesNotExist:
					raise GraphQLError('exam ID is incorrect')

				if ExamFollowerRelation.objects.filter(exam=exam_obj,follower=info.context.user.nxtgenuser).exists():
					raise GraphQLError('you are already following this exam.')

				exam_follower_obj = ExamFollowerRelation.objects.create(exam=exam_obj,follower=info.context.user.nxtgenuser)

				return ExamFollowMutation(exam_follower=exam_follower_obj)


			if input.get('mutation_option') == 3:
				if input.get('exam_follower_id') is None:
					raise GraphQLError('provide proper information')

				try:
					exam_follower_obj = ExamFollowerRelation.objects.select_related('follower').get(
						id=from_global_id(input.get('exam_follower_id'))[1]
						)
				except ExamFollowerRelation.DoesNotExist:
					raise GraphQLError('exam follower ID is incorrect')

				if exam_follower_obj.follower != info.context.user.nxtgenuser:
					raise GraphQLError('you don\'t follow this exam')

				exam_follower_obj.delete()

				return ExamFollowMutation(exam_follower=None)


		else:
			raise GraphQLError('you are not a authenticated user.')
 

class ExamContentMutation(relay.ClientIDMutation):
	exam_post = graphene.Field(ExamPostNode)
	exam_query = graphene.Field(ExamQueryNode)

	class Input:
		exam_content_name = graphene.String(required=True)
		exam_content_id = graphene.ID(required=True)
		block_comment = graphene.Boolean()
		tags = graphene.String()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def exam_content_mapping(exam_content_name,exam_content_obj=None):
			if exam_content_name == 'exam_post':
				return ExamContentMutation(exam_post=exam_content_obj)

			if exam_content_name == 'exam_query':
				return ExamContentMutation(exam_query=exam_content_obj)


		exam_content_names = ('exam_post','exam_query')

		if input.get('mutation_option') not in (2,3):
			raise GraphQLError('provide proper value')

		if input.get('exam_content_name') not in exam_content_names:
			raise GraphQLError('provide proper value')

		if input.get('exam_content_name') == 'exam_post':
			try:
				exam_content_obj = ExamPost.objects.select_related('author').get(id=from_global_id(input.get('exam_post'))[1])
			except ExamPost.DoesNotExist:
				raise GraphQLError('exam post ID is incorrect')

		if input.get('exam_content_name') == 'exam_query':
			try:
				exam_content_obj = ExamQuery.objects.select_related('author').get(id=from_global_id(input.get('exam_query'))[1])
			except ExamQuery.DoesNotExist:
				raise GraphQLError('exam query ID is incorrect')

		if info.context.user.is_authenticated and info.context.user.is_active:
			if exam_content_obj.author != info.context.user.nxtgenuser:
				raise GraphQLError('you are not the author of this content')

			if input.get('mutation_option') == 2:
				if input.get('block_comment') is not None:
					exam_content_obj.block_comment = input.get('block_comment')
					exam_content_obj.save()

				if input.get('tags') is not None:
					json_string = input.get('tags')
					json_data = json.loads(json_string)
					tags = json_data['tags']

					if len(tags) <= 5:
						exam_content_obj.tags.clear()
						for tag in tags:
							exam_content_obj.tags.add(tag)

				exam_content_mapping(input.get('exam_content_name'),exam_content_obj)

			if input.get('mutation_option') == 3:
				exam_content_obj.delete()

				exam_content_mapping(input.get('exam_content_name'))

		else:
			raise GraphQLError('you are not authenticated!!')


class ExamQueryExplanationMutation(relay.ClientIDMutation):
	exam_query_explanation = graphene.Field(ExamQueryExplanationNode)

	class Input:
		exam_query_explanation_id = graphene.ID(required=True)
		explanation = graphene.String()
		status = graphene.String()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (2,3):
			raise GraphQLError('provide proper value')

		try:
			exam_query_explanation_obj = ExamQueryExplanation.objects.select_related('explanation__author').get(
				id=from_global_id(input.get('exam_query_explanation_id'))[1]
				)
		except ExamQueryExplanation.DoesNotExist:
			raise GraphQLError('exam query explanation ID is incorrect')

		if info.context.user.nxtgenuser != exam_query_explanation_obj.explanation.author:
			raise GraphQLError('you are not the author of this explanation')

		if input.get('mutation_option') == 2:
			if input.get('explanation') is not None:
				json_string = input.get('explanation')
				json_data = json.loads(json_string)
				exam_query_explanation_obj.explanation.body = json_data

			if input.get('status') is not None:
				if exam_query_explanation_obj.status == 'draft':
					if input.get('status') == 'active':
						exam_query_explanation_obj.status = 'active'
						exam_query_explanation_obj.publish = timezone.now()

			exam_query_explanation_obj.save()

			return ExamQueryExplanationMutation(exam_query_explanation=exam_query_explanation_obj)


		if input.get('mutation_option') == 3:

			exam_query_explanation_obj.explanation.delete()

			return ExamQueryExplanationMutation(exam_query_explanation=None)


class ExamCommentMutation(relay.ClientIDMutation):
	exam_post_comment = graphene.Field(ExamPostCommentNode)
	exam_query_comment = graphene.Field(ExamQueryCommentNode)
	exam_query_explanation_comment = graphene.Field(ExamQueryExplanationCommentNode)
	test_comment = graphene.Field(TestCommentNode)

	class Input:
		body = graphene.String(required=True)
		it_self = graphene.String()
		comment_on_name = graphene.String(required=True)
		comment_on_id = graphene.ID(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		comment_on_names = ('exam_post','exam_query','exam_query_explanation','test')

		def comment_on_mapping(comment_on_name,comment_obj=None,comment_on_id=None,it_self_obj=None,*args):
			if comment_on_name == 'exam_post':
				if 'return' in args:
					try:
						exam_post_comment_obj = ExamPostComment.objects.get(comment=comment_obj)
					except ExamPostComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam post')

					return ExamCommentMutation(exam_post_comment=exam_post_comment_obj)

				if 'comment_on_id' in args:
					try:
						exam_post_obj = ExamPost.objects.get(id=from_global_id(comment_on_id)[1])
					except ExamPost.DoesNotExist:
						raise GraphQLError('exam post ID is incorrect')

					if exam_post_obj.block_comment is not True:
						raise GraphQLError('comment is blocked on this post')

					return exam_post_obj

				if 'comment_it_self' in args:
					try:
						exam_post_comment_obj = ExamPostComment.objects.select_related('exam_post').get(comment=it_self_obj)
					except ExamPostComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam post')

					return exam_post_comment_obj.exam_post

			if comment_on_name == 'exam_query':
				if 'return' in args:
					try:
						exam_query_comment_obj = ExamQueryComment.objects.get(comment=comment_obj)
					except ExamQueryComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam query')

					return ExamCommentMutation(exam_query_comment=exam_query_comment_obj)

				if 'comment_on_id' in args:
					try:
						exam_query_obj = ExamQuery.objects.get(id=from_global_id(comment_on_id)[1])
					except ExamQuery.DoesNotExist:
						raise GraphQLError('exam query ID is incorrect')

					if exam_query_obj.block_comment is not True:
						raise GraphQLError('comment is blocked on this query')

					return exam_query_obj

				if 'comment_it_self' in args:
					try:
						exam_query_comment_obj = ExamQueryComment.objects.select_related('exam_query').get(comment=it_self_obj)
					except ExamQueryComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam query')

					return exam_query_comment_obj.exam_query


			if comment_on_name == 'exam_query_explanation':
				if 'return' in args:
					try:
						exam_query_explanation_comment_obj = ExamQueryExplanationComment.objects.get(comment=comment_obj)
					except ExamQueryExplanationComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam query explanation')

					return ExamCommentMutation(exam_query_explanation_comment=exam_query_explanation_comment_obj)

				if 'comment_on_id' in args:
					try:
						exam_query_explanation_obj = ExamQueryExplanation.objects.get(id=from_global_id(comment_on_id)[1])
					except ExamQueryExplanation.DoesNotExist:
						raise GraphQLError('exam query explanation ID is incorrect')

					return exam_query_explanation_obj

				if 'comment_it_self' in args:
					try:
						exam_query_explanation_comment_obj = ExamQueryExplanationComment.objects.select_related('exam_query_explanation').get(comment=it_self_obj)
					except ExamQueryExplanationComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this exam query explanation')

					return exam_query_explanation_comment_obj.exam_query_explanation


			if comment_on_name == 'test':
				if 'return' in args:
					try:
						test_comment_obj = TestComment.objects.get(comment=comment_obj)
					except TestComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this test')

					return ExamCommentMutation(test_comment=test_comment_obj)

				if 'comment_on_id' in args:
					try:
						test_obj = Test.objects.get(id=from_global_id(comment_on_id)[1])
					except Test.DoesNotExist:
						raise GraphQLError('test ID is incorrect')

					return test_obj

				if 'comment_it_self' in args:
					try:
						test_comment_obj = TestComment.objects.select_related('test').get(comment=it_self_obj)
					except TestComment.DoesNotExist:
						raise GraphQLError('this comment doesn\'t belong to this test')

					return test_comment_obj.test




		if input.get('comment_on_name') not in comment_on_names:
			raise GraphQLError('provide proper value')

		if info.context.user.is_authenticated and info.context.user.is_active:
			comment_relation_obj = comment_on_mapping(input.get('comment_on_name'),None,input.get('comment_on_id'),'comment_on_id')

			comment_obj = Comment(body=input.get('body'),author=info.context.user.nxtgenuser)

			if input.get('it_self') is not None:
				try:
					comment_it_self_obj = Comment.objects.get(id=from_global_id(input.get('it_self'))[1])
				except Comment.DoesNotExist:
					raise GraphQLError('comment ID is incorrect')

				comment_it_self_relation_obj = comment_on_mapping(input.get('comment_on_name'),None,None,comment_it_self_obj,'comment_it_self')

				if comment_relation_obj != comment_it_self_relation_obj:
					raise GraphQLError('this comment doesn\'t belong to the same model')

				comment_obj.it_self = comment_it_self_obj

			comment_obj._post_for = 'exam'
			comment_obj._comment_on = input.get('comment_on_name')
			comment_obj._comment_on_obj = comment_relation_obj

			comment_on_mapping(input.get('comment_on_name'),comment_obj,None,None,'return')


		else:
			raise GraphQLError('you are not a authenticated user.')


class TestMutation(relay.ClientIDMutation):
	test = graphene.Field(TestNode)

	class Input:
		exam_id = graphene.ID()
		title = graphene.String()
		class_subject_type = graphene.String()
		class_subject_id = graphene.ID() 
		status = graphene.String()
		test_type = graphene.String()
		marking = graphene.Boolean()
		negative_marking = graphene.Boolean()
		public = graphene.Boolean()
		tags = graphene.String()
		test_id = graphene.ID()

		# 1. test_section / 2. test_question
		question_arrangement = graphene.Int()
		test_question = graphene.String()

		mutation_option = graphene.Int()

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper information')

		if info.context.user.is_authenticated and info.context.user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('exam_id') is None or input.get('class_subject_type') is None or input.get('test_type') is None or\
					input.get('question_arrangement') is None or input.get('test_question') is None:
					raise GraphQLError('provide complete information')

					test_obj = Test()
					test_obj.author = info.context.user.nxtgenuser
					try:
						exam_obj = Exam.objects.get(id=from_global_id(input.get('exam_id'))[1])
						test_obj.exam = exam_obj
					except Exam.DoesNotExist:
						raise GraphQLError('exam ID is incorrect')

					if input.get('class_subject_type') != 'none':
						if input.get('class_subject_id') is None:
							raise GraphQLError('provide complete information')

						if input.get('class_subject_type') == 'subject':
							test_obj.class_subject_type = input.get('class_subject_type')
							try:
								subject_teacher_obj = ClassSubjectTeacherRelation.objects.get(
									id=from_global_id(input.get('class_subject_id'))[1]
									)
							except ClassSubjectTeacherRelation.DoesNotExist:
								raise GraphQLError('subject teacher ID is incorrect')

							result = UserAuthorizeTest(info,'sectionSubjectTeacher',class_subject_teacher_obj=subject_teacher_obj)

							if result['sectionSubjectTeacher'] is not True:
								raise GraphQLError('you are not the approprate user. try different account.')

							test_obj.subject_teacher = subject_teacher_obj


						if input.get('class_subject_type') == 'additional subject':
							test_obj.class_subject_type = input.get('class_subject_type')
							try:
								additional_subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.get(
									id=from_global_id(input.get('class_subject_id'))[1]
									)
							except AdditionalSubjectTeacherRelation.DoesNotExist:
								raise GraphQLError('additional subject teacher ID is incorrect')

							result = UserAuthorizeTest(info,'sectionAdditionalSubjectTeacher',class_additional_subject_teacher_obj=additional_subject_teacher_obj)

							if result['sectionAdditionalSubjectTeacher'] is not True:
								raise GraphQLError('you are not the approprate user. try different account.')

							test_obj.additional_subject_teacher = additional_subject_teacher_obj

					else:
						test_obj.class_subject_type = input.get('class_subject_type')

					if input.get('title') is not None:
						test_obj.title = input.get('title')

					valide_choice = False

					for choice in Test.TEST_TYPE:
						if input.get('test_type') == choice[0]:
							valide_choice = True
							test_obj.test_type = input.get('test_type')
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')

					if input.get('marking') is not None:
						test_obj.marking = input.get('marking')

					if input.get('negative_marking') is not None:
						test_obj.negative_marking = input.get('negative_marking')

					if input.get('public') is not None:
						test_obj.public = input.get('public')

					if input.get('tags') is not None:
						json_string = input.get('tags')
						json_data = json.loads(json_string)
						tags = json_data['tags']

						if len(tags) > 5:
							raise GraphQLError('only 5 tags are allowed.')

						else:
							test_obj._tags = tags

					if input.get('question_arrangement') not in (1,2):
						raise GraphQLError('provide proper value.')

					if input.get('question_arrangement') == 1:
						test_obj._question_arrangement = 'test_section'

						json_string = input.get('test_question')
						json_data = json.loads(json_string)
						test_sections = json_data['section']

						for question in test_sections['test_question']:
							try:
								question_obj = Question.objects.get(id=from_global_id(question['question_id'])[1])
							except Question.DoesNotExist:
								raise GraphQLError('question ID is incorrect')

							try:
								question_explanation_obj = QuestionExplanation.objects.get(
									id=from_global_id(question['question_explanation_id'])[1],question=question_obj
									)
							except QuestionExplanation.DoesNotExist:
								raise GraphQLError('question explanation ID is incorrect')

							question['question_obj'] = question_obj
							question['question_explanation_obj'] = question_explanation_obj


						test_obj._test_sections = test_sections

					if input.get('question_arrangement') == 2:
						test_obj._question_arrangement = 'test_question'

						json_string = input.get('test_question')
						json_data = json.loads(json_string)
						test_questions = json_data['question']

						for question in test_questions:
							try:
								question_obj = Question.objects.get(id=from_global_id(question['question_id'])[1])
							except Question.DoesNotExist:
								raise GraphQLError('question ID is incorrect')

							try:
								question_explanation_obj = QuestionExplanation.objects.get(
									id=from_global_id(question['question_explanation_id'])[1],question=question_obj
									)
							except QuestionExplanation.DoesNotExist:
								raise GraphQLError('question explanation ID is incorrect')

							question['question_obj'] = question_obj
							question['question_explanation_obj'] = question_explanation_obj

					if input.get('status') is not None:
						if input.get('status') == 'active':
							test_obj.status = input.get('status')
							test_obj.publish = timezone.now()

					test_obj._test_questions = test_questions
					test_obj.save()

					return TestMutation(test=test_obj)


			if input.get('mutation_option') in (2,3):
				if input.get('test_id') is None:
					raise GraphQLError('provide complete information')

				try:
					test_obj = Test.objects.select_related('author').get(id=from_global_id(input.get('test_id'))[1])
				except Test.DoesNotExist:
					raise GraphQLError('test ID is incorrect')

				if test_obj.author != info.context.user.nxtgenuser:
					raise GraphQLError('you are not the author of this test.')

				if input.get('mutation_option') == 2:
					if input.get('title') is not None:
						test_obj.title = input.get('title')

					if input.get('status') is not None:
						if input.get('status') == 'active':
							if test_obj.status == 'draft':
								test_obj.status = input.get('status')
								test_obj.publish = timezone.now()

					if input.get('marking') is not None:
						test_obj.marking = input.get('marking')

					if input.get('negative_marking') is not None:
						test_obj.negative_marking = input.get('negative_marking')

					if input.get('tags') is not None:
						json_string = input.get('tags')
						json_data = json.loads(json_string)
						tags = json_data['tags']

						if len(tags) > 5:
							raise GraphQLError('only 5 tags are allowed.')

						else:
							test_obj._tags = tags

					test_obj.save()

					return TestMutation(test=test_obj)


				if input.get('mutation_option') == 3:
					test_obj.delete()

					return TestMutation(test=None)

		else:
			raise GraphQLError('you are not authenticated user.')


class TestSectionMutation(relay.ClientIDMutation):
	test_section = graphene.Field(TestSectionNode)

	class Input:
		test_section_id = graphene.ID(required=True)
		test_id = graphene.ID()
		section = graphene.String()
		position = graphene.Int()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('exam_id') is None or input.get('section') is None or input.get('position') is None:
				raise GraphQLError('provide complete information')

			try:
				test_obj = Test.objects.select_related('author').get(id=from_global_id(input.get('test_id'))[1])
			except Exam.DoesNotExist:
				raise GraphQLError('exam ID is incorrect')

			if test_obj.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t belong to this test')

			test_section_obj = TestSection(test=test_obj,section=input.get('section'),position=input.get('position'))
			test_section_obj.save()

			return TestSectionMutation(test_section=test_section_obj)


		if input.get('mutation_option') in (2,3):
			if input.get('test_section_id') is None:
				raise GraphQLError('provde complete information')

			try:
				test_section_obj = TestSection.objects.select_related('test__author').get(
					id=from_global_id(input.get('test_section_id'))[1]
					)
			except TestSection.DoesNotExist:
				raise GraphQLError('test section ID is incorrect')

			if test_section_obj.test.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t belong to this test')

			if input.get('mutation_option') == 2:
				if input.get('section') is not None:
					test_section_obj.section = input.get('section')

				if input.get('position') is not None:
					test_section_obj.position = input.get('position')

				test_section_obj.save()

				return TestSectionMutation(test_section=test_section_obj)

			if input.get('mutation_option') == 3:
				test_Section_obj.delete()

				return TestSectionMutation(test_section=None)


class TestQuestionMutation(relay.ClientIDMutation):
	test_question = graphene.Field(TestQuestionNode)

	class Input:
		test_id = graphene.ID()
		question_id = graphene.ID()
		explanation_id = graphene.ID()
		position = graphene.Int()
		section_id = graphene.ID()
		positive_marks = graphene.Boolean()
		negative_marks = graphene.Boolean()
		test_question_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('test_id') is None or input.get('question_id') is None or input.get('explanation_id') is None or\
				input.get('position') is None:
				try:
					test_obj = Test.objects.select_related('author').get(id=from_global_id(input.get('test_id'))[1])
				except Test.DoesNotExist:
					raise GraphQLError('test ID is incorrect')

				if test_obj.author != info.context.user.nxtgenuser:
					raise GraphQLError('you don\'t belong to this test')
				
				try:
					question_obj = Question.objects.get(id=from_global_id(input.get('question_id'))[1])
				except Question.DoesNotExist:
					raise GraphQLError('question ID is incorrect')

				try:
					explanation_obj = QuestionExplanation.objects.get(
						id=from_global_id(input.get('explanation_id'))[1],question=question_obj
						)
				except QuestionExplanation.DoesNotExist:
					raise GraphQLError('question explanation ID is incorrect')

				test_question_obj = TestQuestion(
					test=test_obj,question=question_obj,explanation=explanation_obj,position=input.get('position')
					)

				if input.get('section_id') is not None:
					try:
						test_section_obj = TestSection.objects.select_related('test').get(
							id=from_global_id(input.get('section_id'))[1]
							)
					except TestSection.DoesNotExist:
						raise GraphQLError('test section ID is incorrect')

					if test_obj != test_section_obj.test:
						raise  GraphQLError('section doesn\'t belong to the same test.')

					test_question_obj.section = test_section_obj

				if input.get('positive_marks') is not None:
					test_question_obj.positive_marks = input.get('positive_marks')

				if input.get('negative_marks') is not None:
					test_question_obj.negative_marks = input.get('negative_marks')

				test_question_obj.save()

				return TestQuestionMutation(test_question=test_question_obj)


		if input.get('mutation_option') in (2,3):
			if input.get('test_question_id') is None:
				raise GraphQLError('provide complete information')

			try:
				test_question_obj = TestQuestion.objects.select_related('test__author').get(
					id=from_global_id(input.get('test_question_id'))[1]
					)
			except TestQuestion.DoesNotExist:
				raise GraphQLError('test question ID is incorrect')

			if test_question_obj.test.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t belong to this test question')

			if input.get('mutation_option') == 2:
				if input.get('explanation_id') is not None:
					try:
						question_explanation_obj = QuestionExplanation.objects.get(
							id=from_global_id(input.get('explanation_id'))[1],question=test_question_obj.question
							)
					except QuestionExplanation.DoesNotExist:
						raise GraphQLError('question explanation ID is incorrect')

					test_question_obj.explanation = question_explanation_obj

				if input.get('position') is not None:
					test_question_obj.position = input.get('position')

				if input.get('section_id') is not None:
					try:
						test_section_obj = TestSection.objects.get(
							id=from_global_id(input.get('section_id'))[1],test=test_question_obj.test
							)
					except TestSection.DoesNotExist:
						raise GraphQLError('test section ID is incorrect')

					test_question_obj.section = test_section_obj

				if input.get('positive_marks') is not None:
					test_question_obj.positive_marks = input.get('positive_marks')

				if input.get('negative_marks') is not None:
					test_question_obj.negative_marks = input.get('negative_marks')

				return TestQuestionMutation(test_question=test_question_obj)


			if input.get('mutation_option') == 3:
				test_question_obj.save()

				return TestQuestionMutation(test_question=None)


class TestQuestionChoiceMutation(relay.ClientIDMutation):
	test_question_choice = graphene.Field(TestQuestionChoiceNode)

	class Input:
		test_question_id = graphene.ID()
		choice = graphene.String()
		correct = graphene.Boolean()
		test_question_choice_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('test_question_id') is None or input.get('choice') is None:
				raise GraphQLError('provide complete information')

			try:
				test_question_obj = TestQuestion.objects.select_related('test__author').get(
					id=from_global_id(input.get('test_question_id'))[1]
					)
			except TestQuestion.DoesNotExist:
				raise GraphQLError('test question ID is incorrect')

			if test_question_obj.test.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t belong to this test')

			test_question_choice_obj = TestQuestionChoice(test_question=test_question_obj,choice=input.get('choice'))

			if input.get('correct') is not None:
				test_question_choice_obj.correct = input.get('correct')

			test_question_choice_obj.save()

			return TestQuestionChoiceMutation(test_question_choice=test_question_choice_obj)

		if input.get('mutation_option') in (2,3):
			if input.get('test_question_choice_id') is None:
				raise GraphQLError('provide complete information')

			try:
				test_question_choice_obj = TestQuestionChoice.objects.select_related('test_question__test__author').get(
					id=from_global_id(input.get('test_question_choice_id'))[1]
					)
			except TestQuestionChoice.DoesNotExist:
				raise GraphQLError('test question choice ID is incorrect')

			if test_question_choice_obj.test_question.test.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t belong to this test question')

			if input.get('mutation_option') == 2:
				if input.get('choice') is not None:
					test_question_choice_obj.choice = input.get('choice')

				if input.get('correct') is not None:
					test_question_choice_obj.correct = input.get('correct')

				test_question_choice_obj.save()

				return TestQuestionChoiceMutation(test_question_choice=test_question_choice_obj)

			if input.get('mutation_option') == 3:
				test_question_choice_obj.delete()

				return TestQuestionChoiceMutation(test_question_choice=None)


class TestStudentMutation(relay.ClientIDMutation):
	test_student = graphene.Field(TestStudentNode)

	class Input:
		test_id = graphene.ID()
		class_student_type = graphene.String()
		class_student_id = graphene.ID()
		test_student_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		nxtgen_user = info.context.user.nxtgenuser
		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')


		if input.get('mutation_option') == 1:
			if input.get('test_id') is None:
				raise GraphQLError('provide complete value')

			test_student_obj = TestStudent()

			try:
				test_obj = Test.objects.get(id=from_global_id(input.get('test_id'))[1])
			except Test.DoesNotExist:
				raise GraphQLError('test ID is incorrect')

			test_student_obj.test = test_obj

			if input.get('class_student_type') is not None:
				if input.get('class_student_id') is None:
					raise GraphQLError('provide complete value')

				valide_choice = False

				for choice in TestStudent.STUDENT_TYPE:
					if input.get('class_student_type') == choice[0]:
						valide_choice = True
						test_student_obj.student_type = input.get('class_student_type')
						break

				if valide_choice is False:
					raise GraphQLError('provie valide label value')

				if input.get('class_student_type') == 'subject':
					try:
						class_student_subject_obj = ClassStudentSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('class_student_id'))[1],
							class_subject_teacher_relation=test_obj.subject_teacher
							)
					except ClassStudentSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('class subject form ID is incorrect')

					test_student_obj.subject_student = class_student_subject_obj

				if input.get('class_student_type') == 'additional subject':
					try:
						class_student_additional_subject_obj = ClassStudentAdditionalSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('class_student_id'))[1],
							class_additional_subject_teacher_relation=test_obj.additional_subject_teacher
							)
					except ClassStudentAdditionalSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('class additional subject form ID is incorrect')

					test_student_obj.additional_subject_student = class_student_additional_subject_obj


			if TestStudent.objects.filter(test=test_obj, student=nxtgen_user).exists():
				raise GraphQLError('you have already taken this test before!!')

			test_student_obj.student = nxtgen_user
			test_student_obj.save()

			return TestStudentMutation(test_student=test_student_obj)


		if input.get('mutation_option') == 3:
			if input.get('test_student_id') is None:
				raise GraphQLError('provide complete value')

			try:
				test_student_obj = TestStudent.objects.select_related('student').get(
					id=from_global_id(input.get('test_student_id'))[1]
					)
			except TestStudent.DoesNotExist:
				raise GraphQLError('test student ID is incorrect')

			if test_student_obj.student != nxtgen_user:
				raise GraphQLError('you don\'t belong to this test')

			test_student_obj.delete()

			return TestStudentMutation(test_student=test_student_obj)


class TestStudentAttemptMutation(relay.ClientIDMutation):
	test_student_attempt = graphene.Field(TestStudentAttemptNode)

	class Input:
		test_student_id = graphene.ID()
		duration_in_minute = graphene.Int()
		total_marks = graphene.Int()
		completed = graphene.Boolean()
		test_student_attempt_id = graphene.ID()
		mutation_option = graphene.Int()

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		nxtgen_user = info.context.user.nxtgenuser
		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('test_student_id') is None or input.get('duration_in_minute') is None:
				raise GraphQLError('provide complete information')

			try:
				test_student_obj = TestStudent.objects.get(
					id=from_global_id(input.get('test_student_id'))[1],student=nxtgen_user
					)
			except TestStudent.DoesNotExist:
				raise GraphQLError('test student ID is incorrect')

			test_student_attempt_obj = TestStudentAttempt(
				test_question=test_student_obj,duration_in_minute=input.get('duration_in_minute')
				)

			if input.get('total_marks') is not None:
				test_student_attempt_obj.total_marks = input.get('total_marks')

			if input.get('completed') is not None:
				test_student_attempt_obj.completed = input.get('completed')

			test_student_attempt_obj.save()

			return TestStudentAttemptMutation(test_student_attempt=test_student_attempt_obj)

		if input.get('mutation_option') == 3:
			if input.get('test_student_attempt_id') is None:
				raise GraphQLError('provide complete information')

			try:
				test_student_attempt_obj = TestStudentAttempt.objects.select_related('test_student__student').get(
					id=from_global_id(input.get('test_student_attempt_id'))[1]
					)
			except TestStudentAttempt.DoesNotExist:
				raise GraphQLError('test student attempt ID is incorrect')

			if test_student_attempt_obj.test_student.student != nxtgen_user:
				raise GraphQLError('you don\'t belong to this test')

			test_student_attempt_obj.delete()

			return TestStudentAttemptMutation(test_student_attempt=None)


class TestQuestionStudentChoiceMutation(relay.ClientIDMutation):
	test_question_student_choice = graphene.Field(TestQuestionStudentChoiceNode)

	class Input:
		attemted_student_id = graphene.ID(required=True)
		question_choice_id = graphene.ID(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		nxtgen_user = info.context.user.nxtgenuser

		try:
			attemted_student_obj = TestStudentAttempt.objects.select_related('test_student__student').get(
				id=from_global_id(input.get('attemted_student_id'))[1]
				)
		except TestStudentAttempt.DoesNotExist:
			raise GraphQLError('attempted student ID is incorrect')

		if attemted_student_obj.test_student.student != nxtgen_user:
			raise GraphQLError('you haven\'t attemted this test')

		try:
			test_question_choice_obj = TestQuestionChoice.objects.select_related('test_question__test').get(
				id=from_global_id(input.get('attemted_student_id'))[1]
				)
		except TestQuestionChoice.DoesNotExist:
			raise GraphQLError('test question choice ID is incorrect')

		if test_question_choice_obj.test_question.test != attemted_student_obj.test_student.test:
			raise GraphQLError('you haven\'t attemted this test.')

		test_question_student_choice_obj = TestQuestionStudentChoice.objects.create(
			question_choice=test_question_choice_obj,attempted_student=attemted_student_obj
			)

		return TestQuestionStudentChoiceMutation(test_question_student_choice=test_question_student_choice_obj)



class TestQuestionStudentExplanationMutation(relay.ClientIDMutation):
	test_question_student_explanation = graphene.Field(TestQuestionStudentExplanationNode)

	class Input:
		attempted_student_id = graphene.ID(required=True)
		test_question_id = graphene.ID(required=True)
		explanation = graphene.String(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		nxtgen_user = info.context.user.nxtgenuser

		try:
			attemted_student_obj = TestStudentAttempt.objects.select_related('test_student__student').get(
				id=from_global_id(input.get('attemted_student_id'))[1]
				)
		except TestStudentAttempt.DoesNotExist:
			raise GraphQLError('attempted student ID is incorrect')

		if attemted_student_obj.test_student.student != nxtgen_user:
			raise GraphQLError('you haven\'t attemted this test')


		try:
			test_question_obj = TestQuestion.objects.select_related('test').get(
				id=from_global_id(input.get('test_question_id'))[1]
				)
		except TestQuestion.DoesNotExist:
			raise GraphQLError('test question ID is incorrect')

		if test_question_obj.test != attemted_student_obj.test_student.test:
			raise GraphQLError('you haven\'t taken this test')

		json_string = input.get('explanation')
		json_data = json.loads(json_string)

		test_question_student_explanation_obj = TestQuestionStudentExplanation.objects.create(
			attempted_student=attemted_student_obj,question=test_question_obj,explanation=json_data
			)

		return TestQuestionStudentExplanationMutation(test_question_student_explanation=test_question_student_explanation_obj)



class Mutation(graphene.ObjectType):
	exam_mutation = ExamMutation.Field()
	exam_follower_mutation = ExamFollowMutation.Field()
	exam_content_update_delete = ExamContentMutation.Field()
	exam_query_explanation_update_delete = ExamQueryExplanationMutation.Field()
	exam_comment_creation = ExamCommentMutation.Field()
	test_mutation = TestMutation.Field()
	test_section_mutation = TestSectionMutation.Field()
	test_question_mutation = TestQuestionMutation.Field()
	test_question_chocie_mutation = TestQuestionChoiceMutation.Field()
	test_student_mutation = TestStudentMutation.Field()
	test_student_attempt_mutation = TestStudentAttemptMutation.Field()
	test_question_student_chocie_mutation = TestQuestionStudentChoiceMutation.Field()
	test_question_student_explanation_mutation = TestQuestionStudentExplanationMutation.Field()






'''
tags = {
	tags:[]
}


test_section =
{
	section:
	[
		{
			section_name:'',
			position:'',
			test_question:
			[
            	{
					question_id:'',
					question_explanation_id:'',
					position:'',
					positive_marks:'', -optional
					negative_marks:'', -optional
					choices:           -optional
					[
						{
							choice:'',
							correct:''  -optional
						}
					]
            	}
			]
		}

	]
}


test_question =
{
	question:
	[
		{
			question_id:'',
			question_explanation_id:'',
			position:'',
			positive_marks:'',   -optional
			negative_marks:'',   -optional 
			choices:             -optional
			[
				{
					choice:'',
					correct:''  -optional
				}
			]
		}
	]
}


'''
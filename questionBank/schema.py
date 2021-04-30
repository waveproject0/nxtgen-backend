import json
from django.utils import timezone
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest

from course.models import Course, Subject, Topic, SubTopic
from concept.models import Concept
from exam.models import Exam
from Class.models import ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from .models import Question, QuestionExplanation, QuestionConcept, QuestionExam,\
QuestionSubjectRelation, QuestionTopicRelation, QuestionSubtopicRelation



class QuestionNode(DjangoObjectType):
    class Meta:
        model = Question
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionExplanationNode(DjangoObjectType):
    class Meta:
        model = QuestionExplanation
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionConceptNode(DjangoObjectType):
    class Meta:
        model = QuestionConcept
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionExamNode(DjangoObjectType):
    class Meta:
        model = QuestionExam
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionSubjectRelationNode(DjangoObjectType):
    class Meta:
        model = QuestionSubjectRelation
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionTopicRelationNode(DjangoObjectType):
    class Meta:
        model = QuestionTopicRelation
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionSubtopicRelationNode(DjangoObjectType):
    class Meta:
        model = QuestionSubtopicRelation
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
	question = relay.Node.Field(QuestionNode)
	all_question = DjangoFilterConnectionField(QuestionNode)

	question_explanation = relay.Node.Field(QuestionExplanationNode)
	all_question_explanation = DjangoFilterConnectionField(QuestionExplanationNode)

	question_concept = relay.Node.Field(QuestionConceptNode)
	all_question_concept = DjangoFilterConnectionField(QuestionConceptNode)

	question_exam = relay.Node.Field(QuestionExamNode)
	all_question_exam = DjangoFilterConnectionField(QuestionExamNode)

	question_subject = relay.Node.Field(QuestionSubjectRelationNode)
	all_question_subject = DjangoFilterConnectionField(QuestionSubjectRelationNode)

	question_topic = relay.Node.Field(QuestionTopicRelationNode)
	all_question_topic = DjangoFilterConnectionField(QuestionTopicRelationNode)

	question_subTopic = relay.Node.Field(QuestionSubtopicRelationNode)
	all_question_subTopic = DjangoFilterConnectionField(QuestionSubtopicRelationNode)


class QuestionMutation(relay.ClientIDMutation):
	question = graphene.Field(QuestionNode)
	question_subject = graphene.Field(QuestionSubjectRelationNode)
	question_topic = graphene.Field(QuestionTopicRelationNode)
	question_subTopic = graphene.Field(QuestionSubtopicRelationNode)

	class Input:
		question_type = graphene.String()
		status = graphene.String()
		title = graphene.String()
		body = graphene.String()
		tags = graphene.String()
		course_relation_id = graphene.ID()
		question_relation_name = graphene.String(required=True)
		question_relation_id = graphene.ID()
		authority = graphene.String()
		authority_model_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def question_return_mapping(question_relation_name, question_relation_obj=None):
			if question_relation_name == 'qs_subject':
				return QuestionMutation(question_subject=question_relation_obj)

			if question_relation_name == 'qs_topic':
				return QuestionMutation(question_topic=question_relation_obj)

			if question_relation_name == 'qs_sub_topic':
				return QuestionMutation(question_topic=question_relation_obj)

		
		question_relation_names = ('qs_subject','qs_topic','qs_sub_topic')

		if input.get('question_relation_name') not in question_relation_names:
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') not in(1,2,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('question_type') is None or input.get('body') is None:
				raise GraphQLError('provide complete information')

			question_obj = Question(author=info.context.user.nxtgenuser)

			json_string = input.get('body')
			json_data = json.loads(json_string)

			question_obj.body = json_data

			if input.get('title') is not None:
				question_obj.title = input.get('title')


			valide_choice = False
			for choice in Question.QUESTION_TYPE:
				if input.get('question_type') == choice[0]:
					valide_choice = True
					question_obj.question_type = input.get('question_type')
					break

			if valide_choice is False:
				raise GraphQLError('provide proper value')

			if input.get('status') is not None:
				if input.get('status') == 'active':
					question_obj.publish = timezone.now()

			if input.get('authority') is not None and input.get('authority_model_id') is not None:
				if input.get('authority') == 'sectionSubjectTeacher':
					try:
						authority_model_obj = ClassSubjectTeacherRelation.objects.select_related('subject__subject').get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except ClassSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('class subject ID is incorrect')

					result = UserAuthorizeTest(info,'sectionSubjectTeacher',class_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')]:
						question_obj.subject_type = 'subject'
						question_obj.subject_teacher = authority_model_obj

				if input.get('authority') == 'sectionAdditionalSubjectTeacher':
					try:
						authority_model_obj = AdditionalSubjectTeacherRelation.objects.select_related('subject__subject').get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except AdditionalSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('class additional subject ID is incorrect')

					result = UserAuthorizeTest(info,'sectionAdditionalSubjectTeacher',class_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')]:
						question_obj.subject_type = 'additional subject'
						question_obj.subject_teacher = authority_model_obj

				if input.get('question_relation_name') == 'qs_subject':
					question_obj._question_relation_name = input.get('question_relation_name')
					question_obj._course_relation_obj = authority_model_obj.subject.subject
					question_obj.question_in = 'subject'

			
			else:
				if input.get('question_relation_name') == 'qs_subject':
					if input.get('course_relation_id') is None:
						raise GraphQLError('provide complete information')

					question_obj._question_relation_name = input.get('question_relation_name')
					try:
						subject_obj = Subject.objects.get(id=from_global_id(input.get('course_relation_id'))[1])
					except Subject.DoesNotExist:
						raise GraphQLError('subject ID is incorrect')

					question_obj._course_relation_obj = subject_obj
					question_obj.question_in = 'subject'

			
			if input.get('question_relation_name') == 'qs_topic':
				if input.get('course_relation_id') is None:
					raise GraphQLError('provide complete information')

				question_obj._question_relation_name = input.get('question_relation_name')
				try:
					topic_obj = Topic.objects.get(id=from_global_id(input.get('course_relation_id'))[1])
				except Topic.DoesNotExist:
					raise GraphQLError('topic ID is incorrect')
				question_obj._course_relation_obj = topic_obj
				question_obj.question_in = 'topic'

			if input.get('question_relation_name') == 'qs_sub_topic':
				if input.get('course_relation_id') is None:
					raise GraphQLError('provide complete information')

				question_obj._question_relation_name = input.get('question_relation_name')
				try:
					subTopic_obj = SubTopic.objects.get(id=from_global_id(input.get('course_relation_id'))[1])
				except SubTopic.DoesNotExist:
					raise GraphQLError('sub_topic ID is incorrect')
				question_obj._course_relation_obj = subTopic_obj
				question_obj.question_in = 'subTopic'

			question_obj.save()


			if input.get('tags') is not None:
				json_string = input.get('tags')
				json_data = json.loads(json_string)
				tags = json_data['tags']

				if len(tags) <= 5:
					for tag in tags:
						question_obj.tags.add(tag)

			return QuestionMutation(question=question_obj)



		if input.get('mutation_option') == 2:
			if input.get('question_relation_id') is None:
				raise GraphQLError('provide complete information')

			if input.get('question_relation_name') == 'qs_subject':
				try:
					question_relation_obj = QuestionSubjectRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionSubjectRelation.DoesNotExist:
					raise GraphQLError('question subject ID is incorrect')

				question_obj = question_relation_obj.question


			if input.get('question_relation_name') == 'qs_topic':
				try:
					question_relation_obj = QuestionTopicRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionTopicRelation.DoesNotExist:
					raise GraphQLError('question subject ID is incorrect')

				question_obj = question_relation_obj.question


			if input.get('question_relation_name') == 'qs_sub_topic':
				try:
					question_relation_obj = QuestionSubtopicRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionSubtopicRelation.DoesNotExist:
					raise GraphQLError('question subTopic ID is incorrect')

				question_obj = question_relation_obj.question

			if info.context.user.nxtgenuser != question_obj.author:
				raise GraphQLError('you are not the author of this question')

			if input.get('title') is not None:
				question_obj.title = input.get('title')

			if input.get('tags') is not None:
				json_string = input.get('tags')
				json_data = json.loads(json_string)
				tags = json_data['tags']

				if len(tags) <= 5:
					question_obj.tags.clear()
					for tag in tags:
						question_obj.tags.add(tag)

			if input.get('status') is not None:
				if input.get('status') == 'active':
					if question_obj.status == 'draft':
						question_obj.status = input.get('status')
						question_obj.publish = timezone.now()

			question_obj.save()


			question_return_mapping(input.get('question_relation_name'),question_relation_obj)


		if input.get('mutation_option') == 3:

			if input.get('question_relation_name') == 'qs_subject':
				try:
					question_relation_obj = QuestionSubjectRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionSubjectRelation.DoesNotExist:
					raise GraphQLError('question subject ID is incorrect')


			if input.get('question_relation_name') == 'qs_topic':
				try:
					question_relation_obj = QuestionTopicRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionTopicRelation.DoesNotExist:
					raise GraphQLError('question subject ID is incorrect')



			if input.get('question_relation_name') == 'qs_sub_topic':
				try:
					question_relation_obj = QuestionSubtopicRelation.objects.select_related('question__author').get(
						id=from_global_id(input.get('question_relation_id'))[1]
						)
				except QuestionSubtopicRelation.DoesNotExist:
					raise GraphQLError('question subTopic ID is incorrect')


			if info.context.user.nxtgenuser != question_relation_obj.question.author:
				raise GraphQLError('you are not the author of this question')

			question_relation_obj.question.delete()

			question_return_mapping(input.get('question_relation_name'))




class QuestionExplanationMutation(relay.ClientIDMutation):
	question_explanation = graphene.Field(QuestionExplanationNode)

	class Input:
		body = graphene.String()
		status = graphene.String()
		question_explanation_id = graphene.ID(required=True)
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (2,3):
			raise GraphQLError('provide proper value')

		try:
			question_explanation_obj = QuestionExplanation.objects.select_related('explanation__author').get(
				id=from_global_id(input.get('question_explanation_id'))[1]
				)
		except QuestionExplanation.DoesNotExist:
			raise GraphQLError('question explanation ID is incorrect')

		if info.context.user.nxtgenuser != question_explanation_obj.explanation.author:
			raise GraphQLError('you are not the author of this explanation.')

		if input.get('mutation_option') == 2:
			if input.get('body') is not None:
				json_string = input.get('body')
				json_data = json.loads(json_string)

				question_explanation_obj.explanation.body = json_data

			if input.get('status') is not None:
				if input.get('status') == 'active':
					if question_explanation_obj.status == 'draft':
						question_explanation_obj.status = input.get('status')
						question_explanation_obj.publish = timezone.now()

			return QuestionExplanationMutation(question_explanation=question_explanation_obj)

		if input.get('mutation_option') == 3:
			question_explanation_obj.explanation.delete()
			return QuestionExplanationMutation(question_explanation=None)





class QuestionConceptMutation(relay.ClientIDMutation):
	question_concept = graphene.Field(QuestionConceptNode)

	class Input:
		question_id = graphene.ID()
		concept_id = graphene.ID()
		question_concept_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('question_id') is None or input.get('concept_id') is None:
				raise GraphQLError('provide complete information')

			try:
				question_obj = Question.objects.select_related('author').get(
					id=from_global_id(input.get('question_id'))[1]
					)

			except Question.DoesNotExist:
				raise GraphQLError('question doesn\'t exists')

			if info.context.user.nxtgenuser != question_obj.author:
				raise GraphQLError('you are not the author of this question')

			try:
				concept_obj = Concept.objects.get(id=from_global_id(input.get('concept_id'))[1])
			except Concept.DoesNotExist:
				raise GraphQLError('concept ID is incorrect')

			question_concept_tuple = QuestionConcept.objects.get_or_create(question=question_obj,concept=concept_obj)

			return QuestionConceptMutation(question_concept=question_concept_tuple[0])

		if input.get('mutation_option') == 3:
			if input.get('question_concept_id') is None:
				raise GraphQLError('provide complete information')

			try:
				question_concept_obj = QuestionConcept.objects.select_related('question__author').get(
					id=from_global_id(input.get('question_concept_id'))[1]
					)
			except QuestionConcept.DoesNotExist:
				raise GraphQLError('question concept ID is incorrect')

			if info.context.user.nxtgenuser != question_concept_obj.question.author:
				raise GraphQLError('you are not the author of this question')

			question_concept_obj.delete()

			return QuestionConceptMutation(question_concept=None)





class QuestionExamMutation(relay.ClientIDMutation):
	question_exam = graphene.Field(QuestionExamNode)

	class Input:
		question_id = graphene.ID()
		exam_id = graphene.ID()
		question_exam_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('question_id') is None or input.get('exam_id') is None:
				raise GraphQLError('provide complete information')

			try:
				question_obj = Question.objects.select_related('author').get(
					id=from_global_id(input.get('question_id'))[1]
					)

			except Question.DoesNotExist:
				raise GraphQLError('question doesn\'t exists')

			if info.context.user.nxtgenuser != question_obj.author:
				raise GraphQLError('you are not the author of this question')

			try:
				exam_obj = Exam.objects.get(id=from_global_id(input.get('exam_id'))[1])
			except Exam.DoesNotExist:
				raise GraphQLError('exam ID is incorrect')

			question_exam_tuple = QuestionExam.objects.get_or_create(question=question_obj,exam=exam_obj)

			return QuestionExamMutation(question_exam=question_exam_tuple[0])

		if input.get('mutation_option') == 3:
			if input.get('question_exam_id') is None:
				raise GraphQLError('provide complete information')

			try:
				question_exam_obj = QuestionExam.objects.select_related('question__author').get(
					id=from_global_id(input.get('question_exam_id'))[1]
					)
			except QuestionExam.DoesNotExist:
				raise GraphQLError('question exam ID is incorrect')

			if info.context.user.nxtgenuser != question_exam_obj.question.author:
				raise GraphQLError('you are not the author of this question')

			question_exam_obj.delete()

			return QuestionExamMutation(question_exam=None)




class Mutation(graphene.ObjectType):
	question_mutation = QuestionMutation.Field()
	question_explanation_update_delete = QuestionExplanationMutation.Field()
	question_concept_mutation = QuestionConceptMutation.Field()
	question_exam_mutation = QuestionExamMutation.Field()
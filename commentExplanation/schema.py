import json
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest, authorityMapping

from .models import Comment, Explanation
from form.models import AbstractFormQueryExplanation, TopicFormQuery, SubTopicFormQuery
from questionBank.models import Question
from exam.models import ExamQuery


class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = []
        interfaces = (relay.Node, )


class ExplanationNode(DjangoObjectType):
    class Meta:
        model = Explanation
        filter_fields = []
        interfaces = (relay.Node, )



class CommentDeleteMutation(relay.ClientIDMutation):
	comment = graphene.Field(CommentNode)

	class Input:
		comment_id = graphene.ID(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		request = info.context
		if request.user.is_authenticated and request.user.is_active:

			try:
				comment_obj = Comment.objects.get(id=from_global_id(input.get('comment_id'))[1])

			except Comment.DoesNotExist:
				raise GraphQLError('comment ID is incorrect')

			if request.user.nxtgenuser != comment_obj.commenter:
				raise GraphQLError('you don\'t own this comment. try different account')

			comment_obj.delete()

			return CommentDeleteMutation(comment=None)

		else:
			raise GraphQLError('Please make sure you are successfully authenticated and your account is active.')




class ExplanationCreationMutation(relay.ClientIDMutation):
	explanation = graphene.Field(ExplanationNode)

	class Input:
		body = graphene.String(required=True)
		status = graphene.String()
		explanation_for = graphene.String(required=True)
		explanation_for_model_id = graphene.ID(required=True)
		authority = graphene.String(required=True)
		authority_model_id = graphene.ID(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		context = authorityMapping(info, input.get('explanation_for'), input.get('authority'), input.get('authority_model_id'))

		if context['verified']:
			json_string = input.get('body')
			json_data = json.loads(json_string)

			explanation_obj = Explanation(body=json_data,author=info.context.user.nxtgenuser)

			if input.get('explanation_for') in ('explanation_topic_form_query','explanation_sub-topic_form_query'):
				if input.get('status') is not None:
					valide_choice = False
					for choice in AbstractFormQueryExplanation.STATUS_CHOICE:
						if input.get('status') == choice[0]:
							valide_choice = True
							explanation_obj._status = input.get('status')
							break

					if valide_choice is False:
						raise GraphQLError('provie proper value')

				if input.get('explanation_for') == 'explanation_topic_form_query':
					try:
						explanation_for_model_obj = TopicFormQuery.objects.get(
							id=from_global_id(input.get('explanation_for_model_id'))[1]
							)
					except TopicFormQuery.DoesNotExist:
						raise GraphQLError('form query ID is incorrect')

				if input.get('explanation_for') == 'explanation_sub-topic_form_query':
					try:
						explanation_for_model_obj = SubTopicFormQuery.objects.get(
							id=from_global_id(input.get('explanation_for_model_id'))[1]
							)
					except SubTopicFormQuery.DoesNotExist:
						raise GraphQLError('form query ID is incorrect')

				if input.get('authority') in ('sectionSubjectTeacher','sectionStudentSubjectTeacher'):
					if explanation_for_model_obj.subject_teacher != context[input.get('authority')]:
						raise GraphQLError('you don\'t have access to this form query')

				if input.get('authority') in ('sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'):
					if explanation_for_model_obj.additional_subject_teacher != context[input.get('authority')]:
						raise GraphQLError('you don\'t have access to this form query')

#-------------------------------------------------------------------------------------------------------------------

			if input.get('explanation_for') == 'question':
				if input.get('status') is not None:
					valide_choice = False
					for choice in Question.STATUS_CHOICE:
						if input.get('status') == choice[0]:
							valide_choice = True
							explanation_obj._status = input.get('status')
							break

					if valide_choice is False:
						raise GraphQLError('provie proper value')

				try:
					explanation_for_model_obj = Question.objects.get(id=from_global_id(input.get('explanation_for_model_id'))[1])
				except Question.DoesNotExist:
					raise GraphQLError('question ID is incorrect')

#---------------------------------------------------------------------------------------------------------------------
			
			if input.get('explanation_for') == 'exam_query':
				try:
					explanation_for_model_obj = ExamQuery.objects.get(id=from_global_id(input.get('explanation_for_model_id'))[1])
				except ExamQuery.DoesNotExist:
					raise GraphQLError('exam query ID is incorrect')

				if input.get('status') is not None:
					if input.get('status') == 'active':
						explanation_obj._status = 'active'



			explanation_obj._explanation_for = input.get('explanation_for')
			explanation_obj._explanation_for_model_obj = explanation_for_model_obj
			explanation_obj.save()

			return ExplanationCreationMutation(explanation=explanation_obj)






class Mutation(graphene.ObjectType):
	comment_delete = CommentDeleteMutation.Field()
	explanation_create = ExplanationCreationMutation.Field()


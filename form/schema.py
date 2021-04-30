import json
from django.utils import timezone
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest

from .models import Form, FormPost, TopicFormQuery, SubTopicFormQuery, CommentFormPostRelation, CommentTopicFormQueryRelation,\
CommentSubTopicFormQueryRelation, AbstractFormQueryExplanation, ExplanationTopicFormQueryRelation,\
ExplanationSubTopicFormQueryRelation,TopicQueryImproveRequest, SubTopicQueryImproveRequest,\
TopicExplanationImproveRequest, SubTopicExplanationImproveRequest
from Class.models import ClassSectionRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from commentExplanation.models import Comment




class FormNode(DjangoObjectType):
    class Meta:
        model = Form
        filter_fields = []
        interfaces = (relay.Node, )


class FormPostNode(DjangoObjectType):
    class Meta:
        model = FormPost
        filter_fields = []
        interfaces = (relay.Node, )


class CommentFormPostRelationNode(DjangoObjectType):
    class Meta:
        model = CommentFormPostRelation
        filter_fields = []
        interfaces = (relay.Node, )


class TopicFormQueryNode(DjangoObjectType):
    class Meta:
        model = TopicFormQuery
        filter_fields = []
        interfaces = (relay.Node, )



class ExplanationTopicFormQueryRelationNode(DjangoObjectType):
    class Meta:
        model = ExplanationTopicFormQueryRelation
        filter_fields = []
        interfaces = (relay.Node, )


class CommentTopicFormQueryRelationNode(DjangoObjectType):
    class Meta:
        model = CommentTopicFormQueryRelation
        filter_fields = []
        interfaces = (relay.Node, )



class SubTopicFormQueryNode(DjangoObjectType):
    class Meta:
        model = SubTopicFormQuery
        filter_fields = []
        interfaces = (relay.Node, )



class ExplanationSubTopicFormQueryRelationNode(DjangoObjectType):
    class Meta:
        model = ExplanationSubTopicFormQueryRelation
        filter_fields = []
        interfaces = (relay.Node, )


class CommentSubTopicFormQueryRelationNode(DjangoObjectType):
    class Meta:
        model = CommentSubTopicFormQueryRelation
        filter_fields = []
        interfaces = (relay.Node, )



class TopicQueryImproveRequestNode(DjangoObjectType):
    class Meta:
        model = TopicQueryImproveRequest
        filter_fields = []
        interfaces = (relay.Node, )


class SubTopicQueryImproveRequestNode(DjangoObjectType):
    class Meta:
        model = SubTopicQueryImproveRequest
        filter_fields = []
        interfaces = (relay.Node, )


class TopicExplanationImproveRequestNode(DjangoObjectType):
    class Meta:
        model = TopicExplanationImproveRequest
        filter_fields = []
        interfaces = (relay.Node, )


class SubTopicExplanationImproveRequestNode(DjangoObjectType):
    class Meta:
        model = SubTopicExplanationImproveRequest
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
	form = relay.Node.Field(FormNode)
	all_form = DjangoFilterConnectionField(FormNode)

	form_post = relay.Node.Field(FormPostNode)
	all_form_post = DjangoFilterConnectionField(FormPostNode)

	comment_form_post = relay.Node.Field(CommentFormPostRelationNode)
	all_comment_form_post = DjangoFilterConnectionField(CommentFormPostRelationNode)

	topic_form_query = relay.Node.Field(TopicFormQueryNode)
	all_topic_form_query = DjangoFilterConnectionField(TopicFormQueryNode)

	explanation_topic_form_query = relay.Node.Field(ExplanationTopicFormQueryRelationNode)
	all_explanation_topic_form_query = DjangoFilterConnectionField(ExplanationTopicFormQueryRelationNode)

	comment_topic_form_query = relay.Node.Field(CommentTopicFormQueryRelationNode)
	all_comment_topic_form_query = DjangoFilterConnectionField(CommentTopicFormQueryRelationNode)

	subTopic_form_query = relay.Node.Field(SubTopicFormQueryNode)
	all_subTopic_form_query = DjangoFilterConnectionField(SubTopicFormQueryNode)

	explanation_subTopic_form_query = relay.Node.Field(ExplanationSubTopicFormQueryRelationNode)
	all_explanation_subTopic_form_query = DjangoFilterConnectionField(ExplanationSubTopicFormQueryRelationNode)

	comment_subTopic_form_query = relay.Node.Field(CommentSubTopicFormQueryRelationNode)
	all_comment_subTopic_form_query = DjangoFilterConnectionField(CommentSubTopicFormQueryRelationNode)

	topic_improve_request = relay.Node.Field(TopicQueryImproveRequestNode)
	all_topic_improve_request = DjangoFilterConnectionField(TopicQueryImproveRequestNode)

	subTopic_improve_request = relay.Node.Field(SubTopicQueryImproveRequestNode)
	all_subTopic_improve_request = DjangoFilterConnectionField(SubTopicQueryImproveRequestNode)

	topic_explanation_improve_request = relay.Node.Field(TopicExplanationImproveRequestNode)
	all_topic_explanation_improve_request = DjangoFilterConnectionField(TopicExplanationImproveRequestNode)

	subTopic_explanation_improve_request = relay.Node.Field(SubTopicExplanationImproveRequestNode)
	all_subTopic_explanation_improve_request = DjangoFilterConnectionField(SubTopicExplanationImproveRequestNode)




class FormPostUpdateDelete(relay.ClientIDMutation):
	form_post = graphene.Field(FormPostNode)

	class Input:
		form_post_id = graphene.String(required=True)
		title = graphene.String()
		data = graphene.String()
		block_comment = graphene.Boolean()
		public = graphene.Boolean()
		tags = graphene.String()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		try:
			form_post_obj = FormPost.objects.get(id=from_global_id(input.get('form_post_id'))[1])
		except FormPost.DoesNotExist:
			raise GraphQLError('form post ID is incorrect')

		if input.get('mutation_option') in (2,3):
			if form_post_obj.author != info.context.user.nxtgenuser:
				raise GraphQLError('you don\'t own this post. Thus,you don\'t have proper permission')

		else:
			raise GraphQLError('provide vaide information')

		if input.get('mutation_option') == 2:
			if form_post_obj.satus == 'archive':
				raise GraphQLError('you can\'t edite a archive post')

			if input.get('title') is not None:
				form_post_obj.post.title = input.get('title')

			if input.get('data') is not None:
				json_string = input.get('data')
				json_data = json.loads(json_string)
				post = json_data['data']

				form_post_obj.post.data = post

			if input.get('block_comment') is not None:
				form_post_obj.block_comment = input.get('block_comment')

			if input.get('public') is not None:
				if input.get('public'):
					if form_post_obj.post_type != 'class':
						form_post_obj.public = True

				else:
					form_post_obj.public = False

			form_post_obj.save()

			if input.get('tags') is not None:
				json_string = input.get('tags')
				json_data = json.loads(json_string)
				tags = json_data['tags']

				if len(tags) <= 5:
					form_post_obj.tags.clear()
					for tag in tags:
						form_post_obj.tags.add(tag)

			return FormPostUpdateDelete(form_post=form_post_obj)


		if input.get('mutation_option') == 3:
			form_post_obj.delete()

			return FormPostUpdateDelete(form_post=None)



class FormQueryUpdateDelete(relay.ClientIDMutation):
	topic_form_query = graphene.Field(TopicFormQueryNode)
	subTopic_form_query = graphene.Field(SubTopicFormQueryNode)

	class Input:
		form_query_id = graphene.ID(required=True)
		form_query_type = graphene.String(required=True)
		data = graphene.String()
		tags = graphene.String()
		authority_model_id = graphene.ID(required=True)
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('form_query_type') not in ('topic','subTopic'):
			raise GraphQLError('provide proper values')

		if input.get('form_query_type') == 'topic':
			try:
				form_query_obj = TopicFormQuery.objects.get(id=from_global_id(input.get('form_query_id'))[1])
			except TopicFormQuery.DoesNotExist:
				raise GraphQLError('form query ID is incorrect')

		if input.get('form_query_type') == 'subTopic':
			try:
				form_query_obj = SubTopicFormQuery.objects.get(id=from_global_id(input.get('form_query_id'))[1])
			except SubTopicFormQuery.DoesNotExist:
				raise GraphQLError('form query ID is incorrect')

		if input.get('mutation_option') in (2,3):
			try:
				class_section_obj = ClassSectionRelation.objects.get(id=from_global_id(input.get('authority_model_id'))[1])
			except ClassSectionRelation.DoesNotExist:
				raise GraphQLError('section ID is incorrect')

			result = UserAuthorizeTest(info, 'sectionStudent', class_section_obj=class_section_obj)
			if result['sectionStudent'] is not True:
				raise GraphQLError('you don\'t own this post. Thus,you don\'t have proper permission')

		else:
			raise GraphQLError('provide vaide information')

		if input.get('mutation_option') == 2:
			if input.get('data') is not None:
				json_string = input.get('data')
				json_data = json.loads(json_string)
				post = json_data['data']

				form_query_obj.post.data = post
				form_query_obj.save()

			if input.get('tags') is not None:
				json_string = input.get('tags')
				json_data = json.loads(json_string)
				tags = json_data['tags']

				if len(tags) <= 5:
					form_post_obj.tags.clear()
					for tag in tags:
						form_post_obj.tags.add(tag)

			if input.get('form_query_type') == 'topic':
				return FormQueryUpdateDelete(topic_form_query=form_query_obj)

			if input.get('form_query_type') == 'subTopic':
				return FormQueryUpdateDelete(subTopic_form_query=form_query_obj)


		if input.get('mutation_option') == 3:
			form_query_obj.delete()

			if input.get('form_query_type') == 'topic':
				return FormQueryUpdateDelete(topic_form_query=None)

			if input.get('form_query_type') == 'subTopic':
				return FormQueryUpdateDelete(subTopic_form_query=None)



class FormQueryExplanationUpdateDeleteMutation(relay.ClientIDMutation):
	explanation_topic_form_query = graphene.Field(ExplanationTopicFormQueryRelationNode)
	explanation_subTopic_form_query = graphene.Field(ExplanationSubTopicFormQueryRelationNode)

	class Input:
		body = graphene.String()
		status = graphene.String()
		explanation_form_query_name = graphene.String(required=True)
		explanation_form_query_id = graphene.ID(required=True)
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		explanation_form_query_names = ('explanation_topic_form_query','explanation_subTopic_form_query')
		if input.get('explanation_form_query_name') not in explanation_form_query_names:
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') not in (2,3):
			raise GraphQLError('provide proper value')

		if input.get('explanation_form_query_name') == 'explanation_topic_form_query':
			explanation_form_query_obj = ExplanationTopicFormQueryRelation.objects.select_related(
				'explanation__author'
				).get(
				id=from_global_id(input.get('explanation_form_query_id'))[1]
				)

		if input.get('explanation_form_query_name') == 'explanation_subTopic_form_query':
			explanation_form_query_obj = ExplanationSubTopicFormQueryRelation.objects.select_related(
				'explanation__author'
				).get(
				id=from_global_id(input.get('explanation_form_query_id'))[1]
				)

		if explanation_form_query_obj.explanation.author != info.context.user.nxtgenuser:
			raise GraphQLError('you are not the author of this explanation')

		if input.get('mutation_option') == 2:
			if input.get('body') is not None:
				json_string = input.get('body')
				json_data = json.loads(json_string)
				explanation_form_query_obj.explanation.body = json_data

				if input.get('status') is not None:
					if explanation_form_query_obj.status != input.get('status'):
						if input.get('status') == 'active':
							explanation_form_query_obj.status = 'active'
							explanation_form_query_obj.publish = timezone.now()

			explanation_form_query_obj.save()

			if input.get('explanation_form_query_name') == 'explanation_topic_form_query':
				return FormQueryExplanationUpdateDeleteMutation(explanation_topic_form_query=explanation_form_query_obj)

			if input.get('explanation_form_query_name') == 'explanation_subTopic_form_query':
				return FormQueryExplanationUpdateDeleteMutation(explanation_subTopic_form_query=explanation_form_query_obj)


		if input.get('mutation_option') == 3:
			explanation_form_query_obj.delete()

			if input.get('explanation_form_query_name') == 'explanation_topic_form_query':
				return FormQueryExplanationUpdateDeleteMutation(explanation_topic_form_query=None)

			if input.get('explanation_form_query_name') == 'explanation_subTopic_form_query':
				return FormQueryExplanationUpdateDeleteMutation(explanation_subTopic_form_query=None)




class FormCommentMutation(relay.ClientIDMutation):
	form_post = graphene.Field(FormPostNode)
	topic_form_query = graphene.Field(TopicFormQueryNode)
	subTopic_form_query = graphene.Field(SubTopicFormQueryNode)

	class Input:
		body = graphene.String(required=True)
		it_self = graphene.ID()
		form_relation_name = graphene.String(required=True)
		form_relation_id = graphene.ID(required=True)
		authority = graphene.String(required=True)
		authority_model_id = graphene.ID(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		form_relation_names = ('form_post', 'topic_form_query', 'subTopic_form_query')
		authority_names = (
			'sectionSubjectTeacher', 'sectionStudentSubjectTeacher',
			'sectionAdditionalSubjectTeacher', 'sectionStudentAdditionalSubjectTeacher'
			)

		if input.get('form_relation_name') not in form_relation_names:
			raise GraphQLError('provide proper value')

		if input.get('authority') not in authority_names:
			raise GraphQLError('provide proper value')

		

		if input.get('form_relation_name') == 'form_post':
			try:
				form_relation_obj = FormPost.objects.get(id=from_global_id(input.get('form_relation_id'))[1])
			except FormPost.DoesNotExist:
				raise GraphQLError('form post ID is incorrect')

		if input.get('form_relation_name') == 'topic_form_query':
			try:
				form_relation_obj = TopicFormQuery.objects.get(id=from_global_id(input.get('form_relation_id'))[1])
			except TopicFormQuery.DoesNotExist:
				raise GraphQLError('form query ID is incorrect')

		if input.get('form_relation_name') == 'subTopic_form_query':
			try:
				form_relation_obj = SubTopicFormQuery.objects.get(id=from_global_id(input.get('form_relation_id'))[1])
			except SubTopicFormQuery.DoesNotExist:
				raise GraphQLError('form query ID is incorrect')



		if input.get('authority') in ('sectionSubjectTeacher','sectionStudentSubjectTeacher'):
			if form_relation_obj.subject_type != 'subject':
				raise GraphQLError('incorrect form relation')

			try:
				authority_model_obj = ClassSubjectTeacherRelation.objects.get(
					id=from_global_id(input.get('authority_model_id'))[1]
					)
			except ClassSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('subject teacher ID is incorrect')

			if form_relation_obj.subject_teacher != authority_model_obj:
				raise GraphQLError('you don\'t have access to this form relation')

			result = UserAuthorizeTest(info, input.get('authority'), class_subject_teacher_obj=authority_model_obj)


		if input.get('authority') in ('sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'):
			if form_relation_obj.subject_type != 'additional subject':
				raise GraphQLError('incorrect form post')

			try:
				authority_model_obj = AdditionalSubjectTeacherRelation.objects.get(
					id=from_global_id(input.get('authority_model_id'))[1]
					)
			except AdditionalSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('subject teacher ID is incorrect')

			if form_relation_obj.subject_teacher != authority_model_obj:
				raise GraphQLError('you don\'t have access to this form post')

			result = UserAuthorizeTest(info, input.get('authority'), class_subject_teacher_obj=authority_model_obj)

		if result[input.get('authority')] is not True:
			raise GraphQLError('you don\'t have proper permission.try different account.')


		comment_obj = Comment(body=input.get('body'),commenter=info.context.user.nxtgenuser)

		if input.get('it_self') is not None:
			try:
				it_self_obj = Comment.objects.get(id=from_global_id(input.get('it_self'))[1])
			except Comment.DoesNotExist:
				raise GraphQLError('comment ID is incorrect')

			if input.get('form_relation_name') == 'form_post':
				if CommentFormPostRelation.objects.filter(form_post=form_relation_obj,comment=it_self_obj).exists() is not True:
					raise GraphQLError('comment does\'t not belong to the same form post')

			if input.get('form_relation_name') == 'topic_form_query':
				if CommentTopicFormQueryRelation.objects.filter(form_post=form_relation_obj,comment=it_self_obj).exists() is not True:
					raise GraphQLError('comment does\'t not belong to the same form query')

			if input.get('form_relation_name') == 'subTopic_form_query':
				if CommentSubTopicFormQueryRelation.objects.filter(form_post=form_relation_obj,comment=it_self_obj).exists() is not True:
					raise GraphQLError('comment does\'t not belong to the same form query')

			comment_obj.it_self = it_self_obj

		comment_obj._post_for = 'form'
		comment_obj._form_relation_name = input.get('form_relation_name')
		comment_obj._form_relation_obj = form_relation_obj
		comment_obj.save()


		if input.get('form_relation_name') == 'form_post':
			return FormCommentMutation(form_post=form_relation_obj)

		if input.get('form_relation_name') == 'topic_form_query':
			return FormCommentMutation(topic_form_query=form_relation_obj)

		if input.get('form_relation_name') == 'subTopic_form_query':
			return FormCommentMutation(subTopic_form_query=form_relation_obj)



class FormImproveRequestMutation(relay.ClientIDMutation):
	topic_improve_request = graphene.Field(TopicQueryImproveRequestNode)
	subTopic_improve_request = graphene.Field(SubTopicQueryImproveRequestNode)
	topic_explanation_improve_request = graphene.Field(TopicExplanationImproveRequestNode)
	subTopic_explanation_improve_request = graphene.Field(SubTopicExplanationImproveRequestNode)

	class Input:
		message = graphene.String()
		improve_request_id = graphene.ID()
		improve_request_name = graphene.String(required=True)
		improve_request_relation_id = graphene.ID()
		authority = graphene.String()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def return_improve_request_mapping(improve_request_name, improve_request_obj=None):
			if improve_request_name == 'topic_query':
				return FormImproveRequestMutation(topic_improve_request=improve_request_obj)

			if improve_request_name == 'subTopic_query':
				return FormImproveRequestMutation(subTopic_improve_request=improve_request_obj)

			if improve_request_name == 'topic_explanation':
				return FormImproveRequestMutation(topic_explanation_improve_request=improve_request_obj)

			if improve_request_name == 'subTopic_explanation':
				return FormImproveRequestMutation(subTopic_explanation_improve_request=improve_request_obj)
		

		improve_request_names = ('topic_query', 'subTopic_query', 'topic_explanation', 'subTopic_explanation')
		authority_names = (
			'sectionSubjectTeacher', 'sectionStudentSubjectTeacher',
			'sectionAdditionalSubjectTeacher', 'sectionStudentAdditionalSubjectTeacher'
			)

		if input.get('improve_request_name') not in improve_request_names:
			raise GraphQLError('provide proper value')

		if input.get('authority') not in authority_names:
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') == 1:
			if input.get('message') is None or input.get('authority') is None:
				raise GraphQLError('provide proper information')

			if input.get('improve_request_name') == 'topic_query':
				try:
					form_query_obj = TopicFormQuery.objects.get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except TopicFormQuery.DoesNotExist:
					raise GraphQLError('form query ID is incorrect')

				improve_request_obj = TopicQueryImproveRequest(form_query=form_query_obj)

			if input.get('improve_request_name') == 'subTopic_query':
				try:
					form_query_obj = SubTopicFormQuery.objects.get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except SubTopicFormQuery.DoesNotExist:
					raise GraphQLError('form query ID is incorrect')

				improve_request_obj = SubTopicQueryImproveRequest(form_query=form_query_obj)


			if input.get('improve_request_name') == 'topic_explanation':
				try:
					form_query_explanation_obj = ExplanationTopicFormQueryRelation.objects.select_related(
						'topic_form_post'
						).get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except ExplanationTopicFormQueryRelation.DoesNotExist:
					raise GraphQLError('form query explanation ID is incorrect')

				form_query_obj = form_query_explanation_obj.topic_form_post

				improve_request_obj = TopicExplanationImproveRequest(form_explanation=form_query_explanation_obj)


			if input.get('improve_request_name') == 'subTopic_explanation':
				try:
					form_query_explanation_obj = ExplanationSubTopicFormQueryRelation.objects.select_related(
						'subTopic_form_post'
						).get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except ExplanationSubTopicFormQueryRelation.DoesNotExist:
					raise GraphQLError('form query explanation ID is incorrect')

				form_query_obj = form_query_explanation_obj.subTopic_form_post

				improve_request_obj = SubTopicExplanationImproveRequest(form_explanation=form_query_explanation_obj)


			if input.get('authority') in ('sectionSubjectTeacher', 'sectionStudentSubjectTeacher'):
				if form_query_obj.subject_type != 'subject':
					raise GraphQLError('you don\'t belong to this form query.')

				subject_teacher_obj = form_query_obj.subject_teacher

				result = UserAuthorizeTest(info, input.get('authority'), class_subject_teacher_obj=subject_teacher_obj)


			if input.get('authority') in ('sectionAdditionalSubjectTeacher', 'sectionStudentAdditionalSubjectTeacher'):
				if form_query_obj.subject_type != 'additional subject':
					raise GraphQLError('you don\'t belong to this form query.')

				additional_subject_teacher_obj = form_query_obj.additional_subject_teacher

				result = UserAuthorizeTest(info, input.get('authority'), class_additional_subject_teacher_obj=additional_subject_teacher_obj)

			if result[input.get('authority')] is not True:
				raise GraphQLError('you don\'t belong to this subject form. try different account')

			improve_request_obj.message = input.get('message')
			improve_request_obj.save()

			return_improve_request_mapping(input.get('improve_request_name'),improve_request_obj)


		if input.get('mutation_option') == 3:
			if input.get('improve_request_id') is None:
				raise GraphQLError('provide proper information')

			if input.get('improve_request_name') == 'topic_query':
				try:
					improve_request_obj = TopicQueryImproveRequest.objects.select_related('requester').get(
						id=from_global_id(input.get('improve_request_id'))[1]
						) 
				except TopicQueryImproveRequest.DoesNotExist:
					raise GraphQLError('improve request ID is incorrect')

			if input.get('improve_request_name') == 'subTopic_query':
				try:
					improve_request_obj = SubTopicQueryImproveRequest.objects.select_related('requester').get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except SubTopicQueryImproveRequest.DoesNotExist:
					raise GraphQLError('improve request ID is incorrect')

			if input.get('improve_request_name') == 'topic_explanation':
				try:
					improve_request_obj = TopicExplanationImproveRequest.objects.select_related(
						'requester'
						).get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except TopicExplanationImproveRequest.DoesNotExist:
					raise GraphQLError('improve request ID is incorrect')


			if input.get('improve_request_name') == 'subTopic_explanation':
				try:
					improve_request_obj = SubTopicExplanationImproveRequest.objects.select_related(
						'requester'
						).get(
						id=from_global_id(input.get('improve_request_relation_id'))[1]
						) 
				except SubTopicExplanationImproveRequest.DoesNotExist:
					raise GraphQLError('improve request ID is incorrect')

			if improve_request_obj.request != info.context.user.nxtgenuser:
				raise GraphQLError('you have not made this request')


			improve_request_obj.delete()

			return_improve_request_mapping(input.get('improve_request_name'))



class Mutation(graphene.ObjectType):
	form_post_update_delete = FormPostUpdateDelete.Field()
	form_query_update_delete = FormQueryUpdateDelete.Field()
	form_comment_create = FormCommentMutation.Field()
	form_query_explanation_update_delete = FormQueryExplanationUpdateDeleteMutation.Field()
	form_improve_request = FormImproveRequestMutation.Field()





'''
data = {
	data:{}
}

tags = {
	tags:[]
}
'''
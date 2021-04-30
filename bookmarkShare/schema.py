import graphene
from django.db import IntegrityError
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest

from Class.models import ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from date.models import PublicDateInstitutionRelation
from form.models import FormPost
from questionBank.models import Question
from .models import PublicDateBookmark, FormPostBookmark, QuestionBookmark, FormPostShare, QuestionShare


class PublicDateBookmarkNode(DjangoObjectType):
    class Meta:
        model = PublicDateBookmark
        filter_fields = []
        interfaces = (relay.Node, )

class FormPostBookmarkNode(DjangoObjectType):
    class Meta:
        model = FormPostBookmark
        filter_fields = []
        interfaces = (relay.Node, )

class QuestionBookmarkNode(DjangoObjectType):
    class Meta:
        model = QuestionBookmark
        filter_fields = []
        interfaces = (relay.Node, )

class FormPostShareNode(DjangoObjectType):
    class Meta:
        model = FormPostShare
        filter_fields = []
        interfaces = (relay.Node, )

class QuestionShareNode(DjangoObjectType):
    class Meta:
        model = QuestionShare
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
	bookmark_public_date = relay.Node.Field(PublicDateBookmarkNode)
	all_bookmark_public_date = DjangoFilterConnectionField(PublicDateBookmarkNode)

	bookmark_form_post = relay.Node.Field(FormPostBookmarkNode)
	all_bookmark_form_post = DjangoFilterConnectionField(FormPostBookmarkNode)

	bookmark_question = relay.Node.Field(QuestionBookmarkNode)
	all_bookmark_question = DjangoFilterConnectionField(QuestionBookmarkNode)

	share_form_post = relay.Node.Field(FormPostShareNode)
	all_share_form_post = DjangoFilterConnectionField(FormPostShareNode)

	share_question = relay.Node.Field(QuestionShareNode)
	all_share_question = DjangoFilterConnectionField(QuestionShareNode)



class BookmarkMutation(relay.ClientIDMutation):
	public_date = graphene.Field(PublicDateBookmarkNode)
	form_post = graphene.Field(FormPostBookmarkNode)
	question = graphene.Field(QuestionBookmarkNode)

	class Input:
		public_date_id = graphene.ID()
		form_post_id = graphene.ID()
		question_id = graphene.ID()
		bookmark_relation_name = graphene.String(required=True)
		bookmark_relation_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def bookmark_return_mapping(bookmark_relation_name, bookmark_relation_obj=None):
			if input.get('bookmark_relation_name') == 'public_date':
				return BookmarkMutation(public_date=bookmark_relation_obj)

			if input.get('bookmark_relation_name') == 'form_post':
				return BookmarkMutation(form_post=bookmark_relation_obj)

			if input.get('bookmark_relation_name') == 'question':
				return BookmarkMutation(question=bookmark_relation_obj)

		

		bookmark_relation_names = ('public_date','form_post','question')

		if input.get('bookmark_relation_name') not in bookmark_relation_names:
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')

		user = info.context.user
		nextgen_user = user.nxtgenuser

		if user.is_authenticated and user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('bookmark_relation_name') == 'public_date':
					bookmark_relation_obj = PublicDateBookmark(user=nextgen_user)

					if input.get('public_date_id') is None:
						raise GraphQLError('provide public date ID')

					try:
						public_date_obj = PublicDateInstitutionRelation.objects.get(
							id=from_global_id(input.get('public_date_id'))[1]
							)
					except PublicDateInstitutionRelation.DoesNotExist:
						raise GraphQLError('public date ID is incorrect')

					bookmark_relation_obj.public_date = public_date_obj

					try:
						bookmark_relation_obj.save()
					except IntegrityError:
						bookmark_relation_obj = PublicDateBookmark.objects.get(user=nextgen_user,public_date=public_date_obj)

				if input.get('bookmark_relation_name') == 'form_post':
					bookmark_relation_obj = FormPostBookmark(user=nextgen_user)

					if input.get('form_post_id') is None:
						raise GraphQLError('provide form post ID')

					try:
						form_post_obj = FormPost.objects.get(
							id=from_global_id(input.get('form_post_id'))[1]
							)
					except FormPost.DoesNotExist:
						raise GraphQLError('form post ID incorrect')

					bookmark_relation_obj.form_post = form_post_obj

					try:
						bookmark_relation_obj.save()
					except IntegrityError:
						bookmark_relation_obj = FormPostBookmark.objects.get(user=nextgen_user,form_post=form_post_obj)


				if input.get('bookmark_relation_name') == 'question':
					bookmark_relation_obj = QuestionBookmark(user=nextgen_user)

					if input.get('question_id') is None:
						raise GraphQLError('provide question ID')

					try:
						question_obj = Question.objects.get(
							id=from_global_id(input.get('question_id'))[1]
							)
					except Question.DoesNotExist:
						raise GraphQLError('question ID is incorrect')

					bookmark_relation_obj.question = question_obj

					try:
						bookmark_relation_obj.save()
					except IntegrityError:
						bookmark_relation_obj = QuestionBookmark.objects.get(user=nextgen_user,question=question_obj)

				bookmark_return_mapping(input.get('bookmark_relation_name'),bookmark_relation_obj)

			if input.get('mutation_option') == 3:
				if input.get('bookmark_relation_id') is None:
					raise GraphQLError('provide bookmark relation ID')

				if input.get('bookmark_relation_name') == 'public_date':
					try:
						bookmark_relation_obj = PublicDateBookmark.objects.select_related('user').get(
							id=from_global_id(input.get('bookmark_relation_id'))[1]
							)
					except PublicDateBookmark.DoesNotExist:
						raise GraphQLError('public date ID is incorrect')

				if input.get('bookmark_relation_name') == 'form_post':
					try:
						bookmark_relation_obj = FormPostBookmark.objects.select_related('user').get(
							id=from_global_id(input.get('bookmark_relation_id'))[1]
							)
					except FormPostBookmark.DoesNotExist:
						raise GraphQLError('form post ID is incorrect')


				if nextgen_user != bookmark_relation_obj.user:
					raise GraphQLError('you don\'t have access to this bookmark.')


				bookmark_relation_obj.delete()

				bookmark_return_mapping(input.get('bookmark_relation_name'),bookmark_relation_obj=None)




class ShareMutation(relay.ClientIDMutation):
	shared_form_post = graphene.Field(FormPostShareNode)
	shared_question = graphene.Field(QuestionShareNode)

	class Input:
		form_post_id = graphene.ID()
		question_id = graphene.ID()
		share_relation_name = graphene.String(required=True)
		share_relation_id = graphene.ID()
		authority = graphene.String(required=True)
		authority_model_id = graphene.ID(required=True)
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		share_relation_names = ('form_post','question')

		if input.get('share_relation_name') not in share_relation_names:
			raise GraphQLError('provide proper value')

		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper value')


		if input.get('share_relation_name') == 'form_post':
			if input.get('mutation_option') == 1:
				access = (
					'sectionSubjectTeacher','sectionStudentSubjectTeacher',
					'sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'
					)

				if input.get('authority') not in access:
					raise GraphQLError('provide proper value')

				if input.get('form_post_id') is None:
					raise GraphQLError('provide proper value')


				form_post_share_obj = FormPostShare(user=info.context.user.nxtgenuser)

				if input.get('authority') in ('sectionSubjectTeacher','sectionStudentSubjectTeacher'):
					try:
						authority_model_obj = ClassSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except ClassSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('authority ID is incorrect')

					try:
						form_post_obj = FormPost.objects.select_related('subject_teacher').get(
							id=from_global_id(input.get('form_post_id'))[1]
							)
					except FormPost.DoesNotExist:
						raise GraphQLError('form post ID is incorrect')


					if form_post_obj.subject_teacher == authority_model_obj:
						raise GraphQLError('this post already belongs to this form.')

					form_post_share_obj.form_post = form_post_obj
					form_post_share_obj.shared_on_subject = authority_model_obj
					form_post_share_obj.shared_on = 'subject'

					if FormPostShare.objects.filter(form_post=form_post_obj,shared_on_subject=authority_model_obj).exists():
						raise GraphQLError('this post is already is shared in the form')

					result = UserAuthorizeTest(info,input.get('authority'),class_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')] is not True:
						raise GraphQLError('you don\'t belong to this form.')

					try:
						form_post_share_obj.save()
					except IntegrityError:
						form_post_share_obj = FormPostShare.objects.get(
							user=info.context.user.nxtgenuser,form_post=form_post_obj,shared_on_subject=authority_model_obj
							)

				if input.get('authority') in ('sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'):
					try:
						authority_model_obj = AdditionalSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except AdditionalSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('authority ID is incorrect')

					try:
						form_post_obj = FormPost.objects.select_related('additional_subject_teacher').get(
							id=from_global_id(input.get('form_post_id'))[1]
							)
					except FormPost.DoesNotExist:
						raise GraphQLError('form post ID is incorrect')


					if form_post_obj.additional_subject_teacher == authority_model_obj:
						raise GraphQLError('this post already belongs to this form.')

					form_post_share_obj.form_post = form_post_obj
					form_post_share_obj.shared_on_additional_subject = authority_model_obj
					form_post_share_obj.shared_on = 'additional subject'

					if FormPostShare.objects.filter(form_post=form_post_obj,shared_on_additional_subject=authority_model_obj).exists():
						raise GraphQLError('this post is already is shared in the form')

					result = UserAuthorizeTest(info,input.get('authority'),class_additional_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')] is not True:
						raise GraphQLError('you don\'t belong to this form.')

					try:
						form_post_share_obj.save()
					except IntegrityError:
						form_post_share_obj = FormPostShare.objects.get(
							user=info.context.user.nxtgenuser,form_post=form_post_obj,shared_on_additional_subject=authority_model_obj
							)

				if form_post_obj.public is not True:
					raise GraphQLError('only public form post can be shared.')

				return ShareMutation(shared_form_post=form_post_share_obj)


			if input.get('mutation_option') == 3:
				if input.get('share_relation_id') is None:
					raise GraphQLError('provide proper value')

				try:
					share_relation_obj = FormPostShare.objects.select_related('user').get(
						id=from_global_id(input.get('share_relation_id'))[1]
						)

				except FormPostShare.DoesNotExist:
					raise GraphQLError('shared form post doesn\'t exists')

				if share_relation_obj.user != info.context.user.nxtgenuser:
					raise GraphQLError('you haven\'t shared this post.')

				share_relation_obj.delete()

				return ShareMutation(shared_form_post=None)

#-------------------------------------------------------------------------------------------------------------

		if input.get('share_relation_name') == 'question':
			if input.get('mutation_option') == 1:
				access = (
					'sectionSubjectTeacher','sectionStudentSubjectTeacher',
					'sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'
					)

				if input.get('authority') not in access:
					raise GraphQLError('provide proper value')

				if input.get('question_id') is None:
					raise GraphQLError('provide proper value')


				question_share_obj = QuestionShare(user=info.context.user.nxtgenuser)

				if input.get('authority') in ('sectionSubjectTeacher','sectionStudentSubjectTeacher'):
					try:
						authority_model_obj = ClassSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except ClassSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('authority ID is incorrect')

					try:
						question_obj = Question.objects.select_related('subject_teacher').get(
							id=from_global_id(input.get('question_id'))[1]
							)
					except Question.DoesNotExist:
						raise GraphQLError('question ID is incorrect')


					if question_obj.subject_teacher == authority_model_obj:
						raise GraphQLError('this question already belongs to this form.')

					question_share_obj.question = question_obj
					question_share_obj.shared_on_subject = authority_model_obj
					question_share_obj.shared_on = 'subject'

					if QuestionShare.objects.filter(question=question_obj,shared_on_subject=authority_model_obj).exists():
						raise GraphQLError('this question is already shared in the form')

					result = UserAuthorizeTest(info,input.get('authority'),class_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')] is not True:
						raise GraphQLError('you don\'t belong to this form.')

					try:
						question_share_obj.save()
					except IntegrityError:
						question_share_obj = QuestionShare.objects.get(
							user=info.context.user.nxtgenuser,question=question_obj,shared_on_subject=authority_model_obj
							)



				if input.get('authority') in ('sectionAdditionalSubjectTeacher','sectionStudentAdditionalSubjectTeacher'):
					try:
						authority_model_obj = AdditionalSubjectTeacherRelation.objects.get(
							id=from_global_id(input.get('authority_model_id'))[1]
							)
					except AdditionalSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('authority ID is incorrect')

					try:
						question_obj = Question.objects.select_related('additional_subject_teacher').get(
							id=from_global_id(input.get('question_id'))[1]
							)
					except Question.DoesNotExist:
						raise GraphQLError('question ID is incorrect')


					if question_obj.additional_subject_teacher == authority_model_obj:
						raise GraphQLError('this question already belongs to this form.')

					question_share_obj.form_post = question_obj
					question_share_obj.shared_on_additional_subject = authority_model_obj
					question_share_obj.shared_on = 'additional subject'

					if QuestionShare.objects.filter(question=form_post_obj,shared_on_additional_subject=authority_model_obj).exists():
						raise GraphQLError('this question is already shared in the form')

					result = UserAuthorizeTest(info,input.get('authority'),class_additional_subject_teacher_obj=authority_model_obj)

					if result[input.get('authority')] is not True:
						raise GraphQLError('you don\'t belong to this form.')

					try:
						question_share_obj.save()
					except IntegrityError:
						question_share_obj = QuestionShare.objects.get(
							user=info.context.user.nxtgenuser,question=question_obj,shared_on_additional_subject=authority_model_obj
							)

				return ShareMutation(shared_question=question_share_obj)


			if input.get('mutation_option') == 3:
				if input.get('share_relation_id') is None:
					raise GraphQLError('provide proper value')

				try:
					share_relation_obj = QuestionShare.objects.select_related('user').get(
						id=from_global_id(input.get('share_relation_id'))[1]
						)

				except QuestionShare.DoesNotExist:
					raise GraphQLError('shared question doesn\'t exists')

				if share_relation_obj.user != info.context.user.nxtgenuser:
					raise GraphQLError('you haven\'t shared this post.')

				share_relation_obj.delete()

				return ShareMutation(shared_question=None)



class Mutation(graphene.ObjectType):
	bookmark_mutation = BookmarkMutation.Field()
	share_mutation = ShareMutation.Field()
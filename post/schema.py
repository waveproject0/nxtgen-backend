import json
import datetime
from datetime import date
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest, authorityMapping
from .models import Post

from institution.models import Institution
from department.models import Department
from course.models import SubjectTopicRelation, Topic, SubTopic, TopicSubTopicRelation
from Class.models import Class, ClassSectionRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from form.models import Form, FormPost, AbstractFormQuery, TopicFormQuery, SubTopicFormQuery
from exam.models import Exam


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = []
        interfaces = (relay.Node, )



class PostCreateMutation(relay.ClientIDMutation):
	post = graphene.Field(PostNode)

	class Input:
		title = graphene.String(required=True)
		data = graphene.String(required=True)
		block_comment = graphene.Boolean()
		status = graphene.String()
		archive_date = graphene.String()
		tags = graphene.String()
		exam_id = graphene.ID()

		form = graphene.String()

		post_for = graphene.String(required=True)
		authority = graphene.String(required=True)
		authority_model_id = graphene.String(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		context = authorityMapping(info, input.get('post_for'), input.get('authority'), input.get('authority_model_id'))

		if context['verified']:
			json_string = input.get('data')
			json_data = json.loads(json_string)

			post_obj = Post(title=input.get('title'), data=json_data)

			if input.get('block_comment') is not None:
				post_obj._block_comment = input.get('block_comment')

			
##################################################################################################################

			if input.get('post_for') == 'announcement':
				if input.get('status') is not None:
					if input.get('status') not in ('active'):
						raise GraphQLError('provide a valide status option')

					else:
						post_obj._status = input.get('status')

				if input.get('archive_date') is not None:
					try:
						archive_date = datetime.datetime.strptime(input.get('archive_date'), '%Y-%m-%d').date()
					except ValueError:
						raise GraphQLError('Incorrect data format, should be YYYY-MM-DD')

					if archive_date < date.today():
						raise GraphQLError('archive date can\'t be in past')

					else:
						post_obj._archive_date = archive_date

				post_obj._authority_model_obj = context[input.get('authority')]

#---------------------------------------------------------------
			
			if input.get('post_for') == 'form_post':
				if input.get('form') is None:
					raise GraphQLError('provide form data')

				json_string = input.get('form')
				json_data = json.loads(json_string)
				form_post = json_data['form_post']

				try:
					form_obj = Form.objects.get(id=from_global_id(json_data['form_id'])[1])
					post_obj._form_obj = form_obj
				except Form.DoesNotExist:
					raise GraphQLError('form id is incorrect')

				if 'post_type' in form_post:
					valide_choice = False
					for choice in FormPost.POST_TYPE:
						if form_post['post_type'] == choice[0]:
							valide_choice = True
							break

					if valide_choice is False:
						raise GraphQLError('provie proper value')

					post_obj._post_type = form_post['post_type']

				if 'public' in form_post:
					if form_post['public']:
						post_obj._public = form_post['public']

				if 'tags' in form_post:
					if len(form_post['tags']) > 5:
						raise GraphQLError('tags can\'t exceed more than 5')

					post_obj._tags = form_post['tags']

				if input.get('authority') in ('sectionSubjectTeacher', 'sectionStudentSubjectTeacher'):
					post_obj._subject_obj = context['sectionSubjectTeacher'].subject.subject
					post_obj._section_subject_obj = context['sectionSubjectTeacher']
					class_obj = context['sectionSubjectTeacher'].section.which_division.Class

				if input.get('authority') in ('sectionAdditionalSubjectTeacher', 'sectionStudentAdditionalSubjectTeacher'):
					post_obj._subject_obj = context['sectionAdditionalSubjectTeacher'].subject.subject
					post_obj._section_subject_obj = context['sectionAdditionalSubjectTeacher']
					class_obj = context['sectionAdditionalSubjectTeacher'].section.which_division.Class
					
				post_obj._author = info.context.user.nxtgenuser

				if class_obj != form_obj.Class:
					raise GraphQLError('form doesn\'t belong tothe same class')

#----------------------------------------------------

			if input.get('post_for') in ('topic_form_query','sub-topic_form_query'):
				if input.get('form') is None:
					raise GraphQLError('provide form data')

				json_string = input.get('form')
				json_data = json.loads(json_string)
				form_query = json_data['form_query']

				try:
					form_obj = Form.objects.get(id=from_global_id(json_data['form_id'])[1])
					post_obj._form_obj = form_obj
				except Form.DoesNotExist:
					raise GraphQLError('form id is incorrect')

				if form_query['topic_id'] is None:
					raise GraphQLError('topic id can\'t be none')


				if 'tags' in form_query:
					if len(form_query['tags']) > 5:
						raise GraphQLError('tags can\'t exceed more than 5')

					post_obj._tags = form_query['tags']

				if input.get('authority') == 'sectionStudentSubjectTeacher':
					post_obj._subject_type = 'subject'
					post_obj._subject_teacher_obj = context['sectionSubjectTeacher']
					subject_obj = context['sectionSubjectTeacher'].subject.subject
					class_obj = context['sectionSubjectTeacher'].section.which_division.Class

				if input.get('authority') == 'sectionAdditionalSubjectTeacher':
					post_obj._subject_type = 'additional subjct'
					post_obj._additional_subject_teacher_obj = context['sectionAdditionalSubjectTeacher']
					subject_obj = context['sectionAdditionalSubjectTeacher'].subject.subject
					class_obj = context['sectionAdditionalSubjectTeacher'].section.which_division.Class

				post_obj._author = result['class_student_obj']

				if class_obj != form_obj.Class:
					raise GraphQLError('form doesn\'t belong tothe same class')

				if input.get('post_for') == 'topic_form_query':
					try:
						subject_topic_obj = SubjectTopicRelation.objects.select_related('subject').get(
							id=from_global_id(form_query['topic_id'])[1]
							)
					except SubjectTopicRelation.DoesNotExist:
						raise GraphQLError('Topic ID is incorrect.')

					if subject_obj != subject_topic_obj.subject:
						raise GraphQLError('this topic doesn\'t belong to the given subject')

					post_obj._subject_topic_obj = subject_topic_obj


				if input.get('post_for') == 'sub-topic_form_query':
					try:
						topic_subtopic_obj = TopicSubTopicRelation.objects.select_related('topic').get(
							id=from_global_id(form_query['topic_id'])[1]
							)
					except TopicSubTopicRelation.DoesNotExist:
						raise GraphQLError('sub-topic ID is incorrect')

					if SubjectTopicRelation.objects.filter(subject=subject_obj,topic=topic_subtopic_obj.topic).exists() is not True:
						raise GraphQLError('this sub-topic doesn\'t not belong to the given subject')

					post_obj._topic_subtopic_obj = topic_subtopic_obj

#----------------------------------------------------

			if input.get('post_for') in ('exam_post', 'exam_query'):
				if input.get('exam_id') is None:
					raise GraphQLError('provide complete information')

				if input.get('tags') is not None:
					json_string = input.get('tags')
					json_data = json.loads(json_string)
					tags = json_data['tags']

					if len(tags) > 5:
						raise GraphQLError('you can\'t have more then 5 tags')

					post_obj._tags = tags

				try:
					exam_obj = Exam.objects.get(id=from_global_id(input.get('exam_id'))[1])
					post_obj._exam_obj = exam_obj
				except Exam.DoesNotExist:
					raise GraphQLError('exam ID is incorrect')

				post_obj._author = info.context.user.nxtgenuser

			post_obj._post_for = input.get('post_for')
			post_obj._authority = input.get('authority')
			post_obj.save()

			return PostCreateMutation(post=post_obj)


class Mutation(graphene.ObjectType):
	post_create = PostCreateMutation.Field()







'''
form = {
	form_id:"",

	form_post:{
		post_type:"", - optional
		public:"", - optional
		tags:[] - optional
	}
	form_query:{
		topic_id:"",
		tags:[] - optional
	}
}
'''
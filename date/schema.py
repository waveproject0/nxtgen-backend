import json
import datetime
from datetime import date, timedelta
from taggit.managers import TaggableManager

import graphene
from graphene import String, List
from graphene_django.converter import convert_django_field
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from account.permissions import UserAuthorizeTest

from .models import Date, DateInstitutionRelation, PublicDateInstitutionRelation, DateDepartmentRelation,\
DateClassRelation, DateSectionRelation, DateSubjectTeacherRelation, DateAdditionalSubjectTeacherRelation

from announcement.models import InstitutionAnnouncementRelation, DepartmentAnnouncementRelation,\
ClassAnnouncementRelation, SectionAnnouncementRelation, SubjectTeacherAnnouncementRelation,\
AdditionalSubjectTeacherAnnouncementRelation

from institution.models import Institution
from department.models import Department
from Class.models import Class, ClassSectionRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation

#converting taggable into gaphql support fields
@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return List(String, source='get_tags')


class DateNode(DjangoObjectType):
    class Meta:
        model = Date
        filter_fields = []
        interfaces = (relay.Node, )


class DateInstitutionRelationNode(DjangoObjectType):
    class Meta:
        model = DateInstitutionRelation
        filter_fields = []
        interfaces = (relay.Node, )


class PublicDateInstitutionRelationNode(DjangoObjectType):
    class Meta:
        model = PublicDateInstitutionRelation
        filter_fields = []
        interfaces = (relay.Node, )


class DateDepartmentRelationNode(DjangoObjectType):
    class Meta:
        model = DateDepartmentRelation
        filter_fields = []
        interfaces = (relay.Node, )



class DateClassRelationNode(DjangoObjectType):
    class Meta:
        model = DateClassRelation
        filter_fields = []
        interfaces = (relay.Node, )



class DateSectionRelationNode(DjangoObjectType):
    class Meta:
        model = DateSectionRelation
        filter_fields = []
        interfaces = (relay.Node, )


class DateSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = DateSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )


class DateAdditionalSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = DateAdditionalSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )




class Query(graphene.ObjectType):

	institution_date = relay.Node.Field(DateInstitutionRelationNode)
	all_institution_date = DjangoFilterConnectionField(DateInstitutionRelationNode)

	public_institution_date = relay.Node.Field(PublicDateInstitutionRelationNode)
	all_public_institution_date = DjangoFilterConnectionField(PublicDateInstitutionRelationNode)

	department_date = relay.Node.Field(DateDepartmentRelationNode)
	all_department_date = DjangoFilterConnectionField(DateDepartmentRelationNode)

	class_date = relay.Node.Field(DateClassRelationNode)
	all_class_date = DjangoFilterConnectionField(DateClassRelationNode)

	section_date = relay.Node.Field(DateSectionRelationNode)
	all_section_date = DjangoFilterConnectionField(DateSectionRelationNode)

	subject_teacher_date = relay.Node.Field(DateSubjectTeacherRelationNode)
	all_subject_teacher_date = DjangoFilterConnectionField(DateSubjectTeacherRelationNode)

	additional_subject_teacher_date = relay.Node.Field(DateAdditionalSubjectTeacherRelationNode)
	all_additional_subject_teacher_date = DjangoFilterConnectionField(DateAdditionalSubjectTeacherRelationNode)




class DateMutation(relay.ClientIDMutation):
	institution_date = graphene.Field(DateInstitutionRelationNode)
	department_date = graphene.Field(DateDepartmentRelationNode)
	class_date = graphene.Field(DateClassRelationNode)
	section_date = graphene.Field(DateSectionRelationNode)
	subject_teacher_date = graphene.Field(DateSubjectTeacherRelationNode)
	additional_subject_teacher_date = graphene.Field(DateAdditionalSubjectTeacherRelationNode)


	class Input:
		date = graphene.String()
		repeat = graphene.Boolean()
		label = graphene.String()
		short_title = graphene.String()
		visibility_option = graphene.String()
		tags = graphene.String()
		date_relation_name = graphene.String(required=True)
		authority_relation_id = graphene.ID(required=True)
		date_relation_id = graphene.ID()
		announcement_relation_id = graphene.ID()
		mutation_option = graphene.Int(required=True)



	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		date_relation_names = (
			'institution_date', 'department_date',
			'class_date', 'section_date',
			'subject_teacher_date', 'additional_subject_teacher_date'
			)

		authority = None

		if input.get('mutation_option') not in (1,3):
			raise GraphQLError('provide proper options')

		if input.get('date_relation_name') not in date_relation_names:
			raise GraphQLError('provide proper options')

		else:
			if input.get('date_relation_name') == 'institution_date':
				try:
					authority_relation_obj = Institution.objects.get(id=from_global_id(input.get('authority_relation_id'))[1])
				except Institution.DoesNotExist:
					raise GraphQLError('institution ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = InstitutionAnnouncementRelation.objects.select_related('institution').get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except InstitutionAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.institution:
						raise GraphQLError('announcement doesn\'t not belong to the same institution')

					if DateInstitutionRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

					if input.get('public') is not None:
						valide_choice = False

						for choice in PublicDateInstitutionRelation.VISIBILITY_OPTION:
							if input.get('label') == choice[0]:
								valide_choice = True
								break

						if valide_choice is False:
							raise GraphQLError('provie valide label value')

						if input.get('tags') is None:
							raise GraphQLError('tags can\'t be null')

				authority = 'adminUser'
				result = UserAuthorizeTest(info,authority,institution_obj=authority_relation_obj)


			if input.get('date_relation_name') == 'department_date':
				try:
					authority_relation_obj = Department.objects.get(id=from_global_id(input.get('authority_relation_id'))[1])
				except Department.DoesNotExist:
					raise GraphQLError('department ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = DepartmentAnnouncementRelation.objects.select_related('department').get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except DepartmentAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.department:
						raise GraphQLError('announcement doesn\'t not belong to the same department')

					if DateDepartmentRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

				authority = 'hod'
				result = UserAuthorizeTest(info,authority,department_obj=authority_relation_obj)


			if input.get('date_relation_name') == 'class_date':
				try:
					authority_relation_obj = Class.objects.get(id=from_global_id(input.get('authority_relation_id'))[1])
				except Class.DoesNotExist:
					raise GraphQLError('class ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = ClassAnnouncementRelation.objects.select_related('Class').get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except ClassAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.Class:
						raise GraphQLError('announcement doesn\'t not belong to the same class')

					if DateClassRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

				authority = 'classTeacher'
				result = UserAuthorizeTest(info,authority,class_obj=authority_relation_obj)


			if input.get('date_relation_name') == 'section_date':
				try:
					authority_relation_obj = ClassSectionRelation.objects.get(id=from_global_id(input.get('authority_relation_id'))[1])
				except ClassSectionRelation.DoesNotExist:
					raise GraphQLError('class section ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = SectionAnnouncementRelation.objects.select_related('section').get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except SectionAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.section:
						raise GraphQLError('announcement doesn\'t not belong to the same class')

					if DateSectionRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

				authority = 'sectionTeacher'
				result = UserAuthorizeTest(info,authority,class_section_obj=authority_relation_obj)


			if input.get('date_relation_name') == 'subject_teacher_date':
				try:
					authority_relation_obj = ClassSubjectTeacherRelation.objects.get(id=from_global_id(input.get('authority_relation_id'))[1])
				except ClassSubjectTeacherRelation.DoesNotExist:
					raise GraphQLError('subject teacher ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = SubjectTeacherAnnouncementRelation.objects.select_related('section_subject').get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except SubjectTeacherAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.section_subject:
						raise GraphQLError('announcement doesn\'t not belong to the same class')

					if DateSubjectTeacherRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

				authority = 'sectionSubjectTeacher'
				result = UserAuthorizeTest(info,authority,class_subject_teacher_obj=authority_relation_obj)


			if input.get('date_relation_name') == 'additional_subject_teacher_date':
				try:
					authority_relation_obj = AdditionalSubjectTeacherRelation.objects.get(
						id=from_global_id(input.get('authority_relation_id'))[1]
						)
				except AdditionalSubjectTeacherRelation.DoesNotExist:
					raise GraphQLError('additional subject teacher ID is incorrect')

				if input.get('announcement_relation_id') is not None:
					try:
						announcement_relation_obj = AdditionalSubjectTeacherAnnouncementRelation.objects.select_related(
							'section_additional_subject'
							).get(
							id=from_global_id(input.get('announcement_relation_id'))[1]
							)
					except AdditionalSubjectTeacherAnnouncementRelation.DoesNotExist:
						raise GraphQLError('announcement ID is incorrect')

					if authority_relation_obj != announcement_relation_obj.section_additional_subject:
						raise GraphQLError('announcement doesn\'t not belong to the same class')

					if DateAdditionalSubjectTeacherRelation.objects.filter(announcement=announcement_relation_obj).exists() is True:
						raise GraphQLError('announcement already linked with an existing date')

				authority = 'sectionAdditionalSubjectTeacher'
				result = UserAuthorizeTest(info,authority,class_additional_subject_teacher_obj=authority_relation_obj)


			if result[authority] is not True:
					raise GraphQLError('you are not a valide user. try different account.')

			if input.get('mutation_option') == 1:
				if input.get('date') is None or input.get('label') is None or input.get('short_title') is None:
					raise GraphQLError('provide all required values to create date')

				else:
					json_data = json.loads(input.get('date'))
					date_string_array = json_data['date_string_array']
					date_array = []
					date_obj = Date()

					if len(date_string_array) == 0:
						raise GraphQLError('date array is empty!!')

					if len(date_string_array) > 2:
						raise GraphQLError('only two dates are allowed')

					else:
						if input.get('repeat') is not None:
							date_obj.repeat = input.get('repeat')
							if input.get('repeat'):
								for date in date_string_array:
									try:
										dateElement = datetime.datetime.strptime(date, '%m-%d').date()
										date_array.append(dateElement)
									except ValueError:
										raise GraphQLError('Incorrect data format, should be MM-DD')

						else:
							for date in date_string_array:
								try:
									dateElement = datetime.datetime.strptime(date, '%Y-%m-%d').date()
									date_array.append(dateElement)
								except ValueError:
									raise GraphQLError('Incorrect data format, should be YYYY-MM-DD')

						if len(date_array) == 2:
							if date_array[0] > date_array[1]:
								raise GraphQLError('first date can\'t be greater then second date')

						date_obj.date = date_array


					valide_choice = False

					for choice in Date.DATE_TYPE:
						if input.get('label') == choice[0]:
							valide_choice = True
							break

					if valide_choice is False:
						raise GraphQLError('provie valide label value')

					date_obj.label = input.get('label')
					date_obj.short_title = input.get('short_title')
					date_obj._date_relation_name = input.get('date_relation_name')

					if input.get('announcement_relation_id') is not None:
						date_obj._announcement_relation_obj = announcement_relation_obj

						if input.get('date_relation_name') == 'institution_date':
							if input.get('visibility_option') is not None:
								date_obj._public = True
								date_obj._visibility_option = input.get('visibility_option')

								json_data = json.loads(input.get('tags'))
								tags_array = json_data['tags']

								if len(tags_array) > 5:
									raise GraphQLError('only 5 tags are allowed')

								date_obj._tags = tags_array
					
					date_obj._authority_relation_obj = authority_relation_obj
					date_obj.save()

					if input.get('date_relation_name') == 'institution_date':
						institution_date_obj = DateInstitutionRelation.objects.get(date=date_obj)
						return DateMutation(institution_date=institution_date_obj)

					if input.get('date_relation_name') == 'department_date':
						department_date_obj = DateDepartmentRelation.objects.get(date=date_obj)
						return DateMutation(department_date=department_date_obj)

					if input.get('date_relation_name') == 'class_date':
						class_date_obj = DateClassRelation.objects.get(date=date_obj)
						return DateMutation(class_date=class_date_obj)

					if input.get('date_relation_name') == 'section_date':
						section_date_obj = DateSectionRelation.objects.get(date=date_obj)
						return DateMutation(section_date=section_date_obj)

					if input.get('date_relation_name') == 'subject_teacher_date':
						subject_teacher_date_obj = DateSubjectTeacherRelation.objects.get(date=date_obj)
						return DateMutation(subject_teacher_date=subject_teacher_date_obj)

					if input.get('date_relation_name') == 'additional_subject_teacher_date':
						additional_subject_teacher_date_obj = DateAdditionalSubjectTeacherRelation.objects.get(date=date_obj)
						return DateMutation(additional_subject_teacher_date=additional_subject_teacher_date_obj)



			if input.get('mutation_option') == 3:
				if input.get('date_relation_id') is None:
					raise GraphQLError('provide prover value')

				else:
					if input.get('date_relation_name') == 'institution_date':
						institution_date_obj = DateInstitutionRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						institution_date_obj.date.delete()
						return DateMutation(institution_date=None)

					if input.get('date_relation_name') == 'department_date':
						department_date_obj = DateDepartmentRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						department_date_obj.date.delete()
						return DateMutation(department_date=None)

					if input.get('date_relation_name') == 'class_date':
						class_date_obj = DateClassRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						class_date_obj.date.delete()
						return DateMutation(class_date=None)

					if input.get('date_relation_name') == 'section_date':
						section_date_obj = DateSectionRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						section_date_obj.date.delete()
						return DateMutation(section_date=None)

					if input.get('date_relation_name') == 'subject_teacher_date':
						subject_teacher_date_obj = DateSubjectTeacherRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						subject_teacher_date_obj.date.delete()
						return DateMutation(subject_teacher_date=None)

					if input.get('date_relation_name') == 'additional_subject_teacher_date':
						additional_subject_teacher_date_obj = DateAdditionalSubjectTeacherRelation.objects.select_related('date').get(
							id=from_global_id(input.get('date_relation_id'))[1]
							)
						additional_subject_teacher_date_obj.date.delete()
						return DateMutation(additional_subject_teacher_date=None)


class PublicDateUpdateDelete(relay.ClientIDMutation):
	public_institution_date = graphene.Field(PublicDateInstitutionRelationNode)

	class Input:
		visibility_option = graphene.String()
		tags = graphene.String()
		public_institution_date_id = graphene.ID(required=True)
		mutation_option = graphene.Int(required=True)


	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (2,3):
			raise GraphQLError('provide proper value')

		try:
			public_date_obj = PublicDateInstitutionRelation.objects.select_related('date_institution__institution').get(
				id=from_global_id(input.get('public_institution_date_id'))[1]
				)
		except PublicDateInstitutionRelation.DoesNotExist:
			raise GraphQLError('public institution date ID is incorrect')

		institution_obj = public_date_obj.date_institution.institution

		result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)

		if result['adminUser'] is not True:
			raise GraphQLError('you are not approprate use. try differnt account')

		if input.get('mutation_option') == 2:
			if input.get('visibility_option') is not None:
				valide_choice = False

				for choice in PublicDateInstitutionRelation.VISIBILITY_OPTION:
					if input.get('visibility_option') == choice[0]:
						valide_choice = True
						break

				if valide_choice is False:
					raise GraphQLError('provie valide label value')

				public_date_obj.visibility = input.get('visibility_option')
				public_date_obj.save()

			if input.get('tags') is not None:
				json_data = json.loads(input.get('tags'))
				tags_array = json_data['tags']

				if len(tags_array) <= 5:
					public_date_obj.tags.clear()
					for tag in tags_array:
						public_date_obj.tags.add(tag)

			return PublicDateUpdateDelete(public_institution_date=public_date_obj)

		if input.get('mutation_option') == 3:
			public_date_obj.delete()

			return PublicDateUpdateDelete(public_institution_date=None)






class Mutation(graphene.ObjectType):
	date_mutation = DateMutation.Field()
	public_date_update_delete = PublicDateUpdateDelete.Field()


'''
date = {
	date_string_array:['','']
}

tags = {
	tags:[]
}
'''
import json
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from account.permissions import UserAuthorizeTest
from Class.models import ClassStudentSubjectTeacherRelation, ClassStudentAdditionalSubjectTeacherRelation,\
ClassStudentRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation

from .models import AbstractAttendance, SubjectTeacherAttendance, AdditionalSubjectTeacherAttendance,\
SubjectAttendee, AdditionalSubjectAttendee




class SubjectTeacherAttendanceNode(DjangoObjectType):
    class Meta:
        model = SubjectTeacherAttendance
        filter_fields = []
        interfaces = (relay.Node, )

class AdditionalSubjectTeacherAttendanceNode(DjangoObjectType):
    class Meta:
        model = AdditionalSubjectTeacherAttendance
        filter_fields = []
        interfaces = (relay.Node, )

class SubjectAttendeeNode(DjangoObjectType):
    class Meta:
        model = SubjectAttendee
        filter_fields = []
        interfaces = (relay.Node, )

class AdditionalSubjectAttendeeNode(DjangoObjectType):
    class Meta:
        model = AdditionalSubjectAttendee
        filter_fields = []
        interfaces = (relay.Node, )




class Query(graphene.ObjectType):
    subject_teacher_attendance = relay.Node.Field(SubjectTeacherAttendanceNode)
    all_subject_teacher_attendance = DjangoFilterConnectionField(SubjectTeacherAttendanceNode)

    additional_subject_teacher_attendance = relay.Node.Field(AdditionalSubjectTeacherAttendanceNode)
    all_additional_subject_teacher_attendance = DjangoFilterConnectionField(AdditionalSubjectTeacherAttendanceNode)

    subject_attendee = relay.Node.Field(SubjectAttendeeNode)
    all_subject_attendee = DjangoFilterConnectionField(SubjectAttendeeNode)

    additional_subject_attendee = relay.Node.Field(AdditionalSubjectAttendeeNode)
    all_additional_subject_attendee = DjangoFilterConnectionField(AdditionalSubjectAttendeeNode)



class AttendanceMutation(relay.ClientIDMutation):
	subject_teacher_attendance = graphene.Field(SubjectTeacherAttendanceNode)
	additional_subject_teacher_attendance = graphene.Field(AdditionalSubjectTeacherAttendanceNode)


	class Input:
		teacher_id = graphene.ID()
		attendance_for = graphene.String()
		attendance_type = graphene.String(required=True)
		attendance_id = graphene.ID()
		attendee = graphene.String()
		attendee_id_array = graphene.String()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def teacherStudentRelation(attendance_type, **kwargs):
			#**kwargs = (attendee,teacher_id,subject_teacher_obj,additional_subject_teacher_obj)

			context = {}
			if 'attendee' in kwargs:
				json_data = json.loads(kwargs['attendee'])
				section_student_array = json_data['section_student']
				attendee_obj_array = []

			if attendance_type == 'subject_teacher':
				if 'teacher_id' in kwargs:
					try:
						subject_teacher_obj = ClassSubjectTeacherRelation.objects.get(id=from_global_id(kwargs['teacher_id'])[1])
						context['subject_teacher_obj'] = subject_teacher_obj
					except ClassSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('subject teacher ID is incorrect')

					context['result'] = UserAuthorizeTest(info,'sectionSubjectTeacher',class_subject_teacher_obj=subject_teacher_obj)

				if 'subject_teacher_obj' in kwargs:
					subject_teacher_obj = kwargs['subject_teacher_obj']
					context['result'] = UserAuthorizeTest(info,'sectionSubjectTeacher',class_subject_teacher_obj=subject_teacher_obj)

				if 'attendee' in kwargs:
					for section_student in section_student_array:
						try:
							section_student_obj = ClassStudentRelation.objects.get(id=from_global_id(section_student)[1])
						except ClassStudentRelation.DoesNotExist:
							raise GraphQLError('student ID is incorrect')

						if ClassStudentSubjectTeacherRelation.objects.filter(class_student_relation=section_student_obj, class_subject_teacher_relation=subject_teacher_obj).exists():
							attendee_obj_array.append(section_student_obj)

						else:
							raise GraphQLError('student doesn\'t belong to the subject teacher')

					context['attendee_obj_array'] = attendee_obj_array

				return context


			if attendance_type == 'additional_subject_teacher':
				if 'teacher_id' in kwargs:
					try:
						additional_subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.get(id=from_global_id(kwargs['teacher_id'])[1])
						context['additional_subject_teacher_obj'] = additional_subject_teacher_obj
					except AdditionalSubjectTeacherRelation.DoesNotExist:
						raise GraphQLError('additional subject teacher ID is incorrect')

					context['result'] = UserAuthorizeTest(info,'sectionAdditionalSubjectTeacher',class_additional_subject_teacher_obj=additional_subject_teacher_obj)

				if 'additional_subject_teacher_obj' in kwargs:
					additional_subject_teacher_obj = kwargs['additional_subject_teacher_obj']
					context['result'] = UserAuthorizeTest(info,'sectionAdditionalSubjectTeacher',class_additional_subject_teacher_obj=additional_subject_teacher_obj)

				if 'attendee' in kwargs:
					for section_student in section_student_array:
						try:
							section_student_obj = ClassStudentRelation.objects.get(id=from_global_id(section_student)[1])
						except ClassStudentRelation.DoesNotExist:
							raise GraphQLError('student ID is incorrect')

						if ClassStudentAdditionalSubjectTeacherRelation.objects.filter(class_student_relation=section_student_obj, class_additional_subject_teacher_relation=additional_subject_teacher_obj).exists():
							attendee_obj_array.append(section_student_obj)

						else:
							raise GraphQLError('student doesn\'t belong to the additional subject teacher')

					context['attendee_obj_array'] = attendee_obj_array

				return context



		attendance_types = ('subject_teacher','additional_subject_teacher')

		if input.get('attendance_type') not in attendance_types:
			raise GraphQLError('provide proper value')


		if input.get('attendance_for') is not None:
			valide_choice = False
			for choice in AbstractAttendance.ATTENDANCE_TYPE:
				if input.get('attendance_for') == choice[0]:
					valide_choice = True
					break

			if valide_choice is False:
				raise GraphQLError('provie proper value')


		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper option')

		if input.get('mutation_option') == 1:
			if input.get('teacher_id') is None or input.get('attendance_for') is None or input.get('attendee') is None:
				raise GraphQLError('provide full details to create attendance')

			context = teacherStudentRelation(input.get('attendance_type'),teacher_id=input.get('teacher_id'),attendee=input.get('attendee'))
			authorization = context['result']
			if input.get('attendance_type') == 'subject_teacher':
				if authorization['sectionSubjectTeacher']:
					attendance_obj = SubjectTeacherAttendance(
						attendance_for=input.get('attendance_for'),teacher=context['subject_teacher_obj']
						)

				else:
					raise GraphQLError('you are not the valid user. try different account')

			if input.get('attendance_type') == 'additional_subject_teacher':
				if authorization['sectionAdditionalSubjectTeacher']:
					attendance_obj = AdditionalSubjectTeacherAttendance(
						attendance_for=input.get('attendance_for'),teacher=context['additional_subject_teacher_obj']
						)

				else:
					raise GraphQLError('you are not the valid user. try different account')

			attendance_obj._attendee_obj_array = context['attendee_obj_array']
			attendance_obj.save()

			if input.get('attendance_type') == 'subject_teacher':
				return AttendanceMutation(subject_teacher_attendance=attendance_obj)
			if input.get('attendance_type') == 'additional_subject_teacher':
				return AttendanceMutation(additional_subject_teacher_attendance=attendance_obj)


		if input.get('mutation_option') == 2:
			if input.get('attendance_id') is None:
				raise GraphQLError('provide proper complete value to update attendance')

			if input.get('attendee_id_array') is not None:
				json_data = json.loads(input.get('attendee_id_array'))
				attendee_id_array = json_data['attendee_id_array']

			if input.get('attendance_type') == 'subject_teacher':
				try:
					attendance_obj = SubjectTeacherAttendance.objects.select_related('teacher').get(
						id=from_global_id(input.get('attendance_id'))[1]
						)
				except SubjectTeacherAttendance.DoesNotExist:
					raise GraphQLError('attendance ID is incorrect')

				context = teacherStudentRelation(input.get('attendance_type'),subject_teacher_obj=attendance_obj.teacher)
				authorization = context['result']
				if authorization['sectionSubjectTeacher'] is not True:
					raise GraphQLError('you are not the valid user. try different account')

				# remove existing attendee
				if input.get('attendee_id_array') is not None:
					for attendee_id in attendee_id_array:
						try:
							subject_attendee_obj = SubjectAttendee.objects.get(
								id=from_global_id(attendee_id)[1],attendance=attendance_obj
								)
						except SubjectAttendee.DoesNotExist:
							subject_attendee_obj = None

						if subject_attendee_obj is not None:
							subject_attendee_obj.delete()


				# add new attendee
				if input.get('attendee') is not None:
					attendee = teacherStudentRelation(input.get('attendance_type'),attendee=input.get('attendee'))
					for attendee_obj in attendee['attendee_obj_array']:
						if SubjectAttendee.objects.filter(attendance=attendance_obj,attendee=attendee_obj).exists() is not True:
							SubjectAttendee.objects.create(attendance=attendance_obj,attendee=attendee_obj)


				# changing attendance option
				if input.get('attendance_for') is not None:
					attendance_obj.attendance_for = input.get('attendance_for')
					attendance_obj.save()


				return AttendanceMutation(subject_teacher_attendance=attendance_obj)



			if input.get('attendance_type') == 'additional_subject_teacher':
				try:
					attendance_obj = AdditionalSubjectTeacherAttendance.objects.select_related('teacher').get(
						id=from_global_id(input.get('attendance_id'))[1]
						)
				except AdditionalSubjectTeacherAttendance.DoesNotExist:
					raise GraphQLError('attendance ID is incorrect')

				context = teacherStudentRelation(input.get('attendance_type'),additional_subject_teacher_obj=attendance_obj.teacher)
				authorization = context['result']
				if authorization['sectionAdditionalSubjectTeacher'] is not True:
					raise GraphQLError('you are not the valid user. try different account')

				# remove existing attendee
				if input.get('attendee_id_array') is not None:
					for attendee_id in attendee_id_array:
						try:
							additional_subject_attendee_obj = AdditionalSubjectAttendee.objects.get(
								id=from_global_id(attendee_id)[1],attendance=attendance_obj
								)
						except AdditionalSubjectAttendee.DoesNotExist:
							additional_subject_attendee_obj = None

						if additional_subject_attendee_obj is not None:
							additional_subject_attendee_obj.delete()


				# add new attendee
				if input.get('attendee') is not None:
					attendee = teacherStudentRelation(input.get('attendance_type'),attendee=input.get('attendee'))
					for attendee_obj in attendee['attendee_obj_array']:
						if AdditionalSubjectAttendee.objects.filter(attendance=attendance_obj,attendee=attendee_obj).exists() is not True:
							AdditionalSubjectAttendee.objects.create(attendance=attendance_obj,attendee=attendee_obj)


				# changing attendance option
				if input.get('attendance_for') is not None:
					attendance_obj.attendance_for = input.get('attendance_for')
					attendance_obj.save()



				return AttendanceMutation(additional_subject_teacher_attendance=attendance_obj)




		if input.get('mutation_option') == 3:
			if input.get('attendance_id') is None:
				raise GraphQLError('provide proper complete value to delete attendance')


			if input.get('attendance_type') == 'subject_teacher':
				try:
					attendance_obj = SubjectTeacherAttendance.objects.select_related('teacher').get(
						id=from_global_id(input.get('attendance_id'))[1]
						)
				except SubjectTeacherAttendance.DoesNotExist:
					raise GraphQLError('attendance ID is incorrect')

				context = teacherStudentRelation(input.get('attendance_type'),subject_teacher_obj=attendance_obj.teacher)
				authorization = context['result']
				if authorization['sectionSubjectTeacher'] is not True:
					raise GraphQLError('you are not the valid user. try different account')

				attendance_obj.delete()

				return AttendanceMutation(subject_teacher_attendance=None)


			if input.get('attendance_type') == 'additional_subject_teacher':
				try:
					attendance_obj = AdditionalSubjectTeacherAttendance.objects.select_related('teacher').get(
						id=from_global_id(input.get('attendance_id'))[1]
						)
				except AdditionalSubjectTeacherAttendance.DoesNotExist:
					raise GraphQLError('attendance ID is incorrect')

				context = teacherStudentRelation(input.get('attendance_type'),additional_subject_teacher_obj=attendance_obj.teacher)
				authorization = context['result']
				if authorization['sectionAdditionalSubjectTeacher'] is not True:
					raise GraphQLError('you are not the valid user. try different account')

				attendance_obj.delete()

				return AttendanceMutation(additional_subject_teacher_attendance=None)


			
class Mutation(graphene.ObjectType):
	attendance_mutation = AttendanceMutation.Field()





'''
attendee = {section_student=[]}
attendee_id_array = {attendee_id_array=[]}
'''
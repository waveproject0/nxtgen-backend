from graphql import GraphQLError
from graphql_relay import from_global_id
from django.core.exceptions import ObjectDoesNotExist

from nxtgenUser.models import NxtgenUser
from institution.models import Institution, InstitutionTeacherRelation, InstitutionStudentRelation
from department.models import Department
from Class.models import Class, ClassSectionRelation, ClassStudentRelation, ClassSubjectTeacherRelation,\
ClassStudentSubjectTeacherRelation, AdditionalSubjectTeacherRelation, ClassStudentAdditionalSubjectTeacherRelation




# User Autorization test function,

'''
 *args(
 adminUser, institutionStudent,
 hod, departmentStudent,
 classTeacher, classStudent,
 sectionTeacher, sectionStudent,
 sectionSubjectTeacher, sectionStudentSubjectTeacher,
 sectionAdditionalSubjectTeacher, sectionStudentAdditionalSubjectTeacher

 ) - AllOptional


**kwargs(
institution_obj,department_obj,class_obj,class_section_obj,
class_subject_teacher_obj,class_additional_subject_teacher_obj

) - AllObjects

'''

def UserAuthorizeTest(info, *args, **kwargs):
	request = info.context
	context = {}
	teacher_profile = None
	student_profile = None

	if request.user.is_authenticated and request.user.is_active:
		try:
			teacher_profile = request.user.nxtgenuser.teacherprofile
		except ObjectDoesNotExist:
			teacher_profile = None

		try:
			student_profile = request.user.nxtgenuser.studentprofile
		except ObjectDoesNotExist:
			student_profile = None

		if teacher_profile is None and student_profile is None:
			raise GraphQLError('Your are not approprate user')

		if 'adminUser' in args:
			try:
				institution_teacher_relation_obj = InstitutionTeacherRelation.objects.get(
					institution=kwargs['institution_obj'], teacher=teacher_profile
					)
			except InstitutionTeacherRelation.DoesNotExist:
				raise GraphQLError('You don\'t belong to this institution. please try different account')
			try:
				admin_user = institution_teacher_relation_obj.superadmincontrol
			except:
				raise GraphQLError('You don\'t have AdminUser access for this institution')

			if admin_user.status is False:
				context['adminUser'] = False
			else:
				context['adminUser'] = True

		if 'institutionStudent' in args:
			if InstitutionStudentRelation.objects.filter(institution=kwargs['institution_obj'], student=student_profile).exists():
				context['institutionStudent'] = True
			else:
				context['institutionStudent'] = False


		if 'hod' in args:
			department_hod = kwargs['department_obj'].hod.teacher

			if department_hod == teacher_profile:
				context['hod'] = True
			else:
				context['hod'] = False

		if 'departmentStudent' in args:
			institution_obj = kwargs['department_obj'].institution
			try:
				institution_student_obj = InstitutionStudentRelation.objects.get(
					institution=institution_obj,student=student_profile
					)
			except InstitutionStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to the same institution')

			try:
				class_student_obj = ClassStudentRelation.objects.select_related('section__which_division__Class__department').get(
					student=institution_student_obj
					)
			except ClassStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to any department')

			if kwargs['department_obj'] == class_student_obj.section.which_division.Class.department:
				context['departmentStudent'] = True

			else:
				context['departmentStudent'] = False


		if 'classTeacher' in args:
			class_teacher = kwargs['class_obj'].teacher.teacher

			if class_teacher == teacher_profile:
				context['classTeacher'] = True
			else:
				context['classTeacher'] = False



		if 'classStudent' in args:
			institution_obj = kwargs['class_obj'].institution
			try:
				institution_student_obj = InstitutionStudentRelation.objects.get(
					institution=institution_obj,student=student_profile
					)
			except InstitutionStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to the same institution')

			try:
				class_student_obj = ClassStudentRelation.objects.select_related('section__which_division__Class').get(
					student=institution_student_obj
					)
			except ClassStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to any class')

			if kwargs['class_obj'] == class_student_obj.section.which_division.Class:
				context['classStudent'] = True

			else:
				context['classStudent'] = False



		if 'sectionTeacher' in args:
			section_teacher = kwargs['class_section_obj'].teacher.teacher

			if section_teacher == teacher_profile:
				context['sectionTeacher'] = True
			else:
				context['sectionTeacher'] = False


		if 'sectionStudent' in args:
			institution_obj = kwargs['class_section_obj'].which_division.Class.institution
			try:
				institution_student_obj = InstitutionStudentRelation.objects.get(
					institution=institution_obj,student=student_profile
					)
			except InstitutionStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to the same institution')

			try:
				class_student_obj = ClassStudentRelation.objects.select_related('section').get(
					student=institution_student_obj
					)
			except ClassStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to any section')

			if kwargs['class_section_obj'] == class_student_obj.section:
				context['sectionStudent'] = True

			else:
				context['sectionStudent'] = False



		if 'sectionSubjectTeacher' in args:
			section_subject_teacher = kwargs['class_subject_teacher_obj'].teacher.teacher

			if section_subject_teacher == teacher_profile:
				context['sectionSubjectTeacher'] = True
			else:
				context['sectionSubjectTeacher'] = False



		if 'sectionStudentSubjectTeacher' in args:
			institution_obj = kwargs['class_subject_teacher_obj'].section.which_division.Class.institution
			try:
				institution_student_obj = InstitutionStudentRelation.objects.get(
					institution=institution_obj,student=student_profile
					)
			except InstitutionStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to the same institution')

			try:
				class_student_obj = ClassStudentRelation.objects.get(
					student=institution_student_obj
					)
			except ClassStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to any section')

			if ClassStudentSubjectTeacherRelation.objects.filter(class_student_relation=class_student_obj,class_subject_teacher_relation=kwargs['class_subject_teacher_obj']).exists():
				context['sectionStudentSubjectTeacher'] = True
				context['class_student_obj'] = class_student_obj

			else:
				context['sectionStudentSubjectTeacher'] = False


		if 'sectionAdditionalSubjectTeacher' in args:
			section_additional_subject_teacher = kwargs['class_additional_subject_teacher_obj'].teacher.teacher

			if section_additional_subject_teacher == teacher_profile:
				context['sectionAdditionalSubjectTeacher'] = True
			else:
				context['sectionAdditionalSubjectTeacher'] = False


		if 'sectionStudentAdditionalSubjectTeacher' in args:
			institution_obj = kwargs['class_additional_subject_teacher_obj'].section.which_division.Class.institution
			try:
				institution_student_obj = InstitutionStudentRelation.objects.get(
					institution=institution_obj,student=student_profile
					)
			except InstitutionStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to the same institution')

			try:
				class_student_obj = ClassStudentRelation.objects.get(
					student=institution_student_obj
					)
			except ClassStudentRelation.DoesNotExist:
				raise GraphQLError('student doesn\'t not belong to any section')

			if ClassStudentAdditionalSubjectTeacherRelation.objects.filter(class_student_relation=class_student_obj,class_subject_teacher_relation=kwargs['class_additional_subject_teacher_obj']).exists():
				context['sectionStudentAdditionalSubjectTeacher'] = True
				context['class_student_obj'] = class_student_obj

			else:
				context['sectionStudentAdditionalSubjectTeacher'] = False


		return context

	else:
		raise GraphQLError('Please make sure you are successfully authenticated and your account is active.')











def authorityMapping(info, post_for, authority, authority_model_id):
	authority_roles = (
		'nxtgen_user',
		'adminUser','hod',
		'classTeacher','sectionTeacher',
		'sectionSubjectTeacher',
		'sectionAdditionalSubjectTeacher',
		'sectionStudentSubjectTeacher',
		'sectionStudentAdditionalSubjectTeacher'
		)

	posts_for = (
		'announcement',
		'question',
		'form_post',
		'topic_form_query',
		'sub-topic_form_query',
		'explanation_topic_form_query',
		'explanation_sub-topic_form_query',
		'exam_post',
		'exam_query'
		)

	request = info.context.user
	context = {}

	if authority not in authority_roles:
		raise GraphQLError('provide valide options')

	else:
		if authority == 'nxtgen_user':
			if request.is_authenticated and request.is_active:
				try:
					nxtgen_user_obj = NxtgenUser.objects.get(id=from_global_id(authority_model_id)[1])
				except NxtgenUser.DoesNotExist:
					raise GraphQLError('nxtgen user ID is incorrect')

				if request.nxtgenuser == nxtgen_user_obj:
					result =  True
				else:
					result = False

			else:
				raise GraphQLError('you are not authenticated. try different account.')

		if authority == 'adminUser':
			try:
				institution_obj = Institution.objects.get(id=from_global_id(authority_model_id)[1])
				context['adminUser'] = institution_obj
			except Institution.DoesNotExist:
				raise GraphQLError('institution ID is incorrect')

			result = UserAuthorizeTest(info, authority, institution_obj=institution_obj)

		if authority == 'hod':
			try:
				department_obj = Department.objects.get(id=from_global_id(authority_model_id)[1])
				context['hod'] = department_obj
			except Department.DoesNotExist:
				raise GraphQLError('department ID is incorrect')

			result = UserAuthorizeTest(info, authority, department_obj=department_obj)

		if authority == 'classTeacher':
			try:
				class_obj = Class.objects.get(id=from_global_id(authority_model_id)[1])
				context['classTeacher'] = class_obj
			except Class.DoesNotExist:
				raise GraphQLError('class teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_obj=class_obj)

		if authority == 'sectionTeacher':
			try:
				class_section_obj = ClassSectionRelation.objects.get(id=from_global_id(authority_model_id)[1])
				context['sectionTeacher'] = class_section_obj
			except ClassSectionRelation.DoesNotExist:
				raise GraphQLError('section teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_section_obj=class_section_obj)

		if authority == 'sectionSubjectTeacher':
			try:
				class_subject_teacher_obj = ClassSubjectTeacherRelation.objects.get(id=from_global_id(authority_model_id)[1])
				context['sectionSubjectTeacher'] = class_subject_teacher_obj
			except ClassSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('subject teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_subject_teacher_obj=class_subject_teacher_obj)


		if authority == 'sectionStudentSubjectTeacher':
			try:
				class_subject_teacher_obj = ClassSubjectTeacherRelation.objects.get(id=from_global_id(authority_model_id)[1])
				context['sectionSubjectTeacher'] = class_subject_teacher_obj
			except ClassSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('subject teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_subject_teacher_obj=class_subject_teacher_obj)



		if authority == 'sectionAdditionalSubjectTeacher':
			try:
				class_additional_subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.get(id=from_global_id(authority_model_id)[1])
				context['sectionAdditionalSubjectTeacher'] = class_additional_subject_teacher_obj
			except AdditionalSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('additional subject teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_additional_subject_teacher_obj=class_additional_subject_teacher_obj)



		if authority == 'sectionStudentAdditionalSubjectTeacher':
			try:
				class_additional_subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.get(id=from_global_id(authority_model_id)[1])
				context['sectionAdditionalSubjectTeacher'] = class_additional_subject_teacher_obj
			except AdditionalSubjectTeacherRelation.DoesNotExist:
				raise GraphQLError('additional subject teacher ID is incorrect')

			result = UserAuthorizeTest(info, authority, class_additional_subject_teacher_obj=class_additional_subject_teacher_obj)
		


	if post_for not in posts_for:
		raise GraphQLError('provide valide options')

	else:
		if post_for == 'announcement':
			access = ('adminUser','hod','classTeacher','sectionTeacher','sectionSubjectTeacher','sectionAdditionalSubjectTeacher')
			if authority not in access:
				raise GraphQLError('you don\'t have permission to announcement')

			else:
				if result[authority] is not True:
					raise GraphQLError('you are not the valide user. try different account')

				else:
					context['verified'] = True
					return context


		if post_for not in ('question','exam_post','exam_query'):
			access = ('nxtgen_user')
			if authority not in access:
				raise GraphQLError('you don\'t have permission to announcement')

			else:
				if result is not True:
					raise GraphQLError('you are not the valide user. try different account')

				else:
					context['verified'] = True
					return context

		if post_for == 'form_post':
			access = (
				'sectionSubjectTeacher','sectionAdditionalSubjectTeacher',
				'sectionStudentSubjectTeacher','sectionStudentAdditionalSubjectTeacher'
				)

			if authority not in access:
				raise GraphQLError('you don\'t have permission to announcement')

			else:
				if result[authority] is not True:
					raise GraphQLError('you are not the valide user. try different account')

				else:
					context['verified'] = True
					return context


		if post_for in ('topic_form_query','sub-topic_form_query'):
			access = (
				'sectionStudentSubjectTeacher','sectionStudentAdditionalSubjectTeacher'
				)

			if authority not in access:
				raise GraphQLError('you don\'t have permission to announcement')

			else:
				if result[authority] is not True:
					raise GraphQLError('you are not the valide user. try different account')

				else:
					context['verified'] = True
					return context


		if post_for in ('explanation_topic_form_query','explanation_sub-topic_form_query'):
			access = (
				'sectionSubjectTeacher','sectionAdditionalSubjectTeacher',
				'sectionStudentSubjectTeacher','sectionStudentAdditionalSubjectTeacher'
				)

			if authority not in access:
				raise GraphQLError('you don\'t have permission to announcement')

			else:
				if result[authority] is not True:
					raise GraphQLError('you are not the valide user. try different account')

				else:
					context['verified'] = True
					return context
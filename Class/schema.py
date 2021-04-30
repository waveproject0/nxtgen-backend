import json
import datetime

from django.db import IntegrityError

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from account.permissions import UserAuthorizeTest

from department.models import Department
from institution.models import InstitutionTeacherRelation, InstitutionStudentRelation
from course.models import CourseSubjectRelation, Subject

from .models import Class, ClassDivision, ClassWhichDivision, ClassSectionRelation, ClassStudentRelation,\
SessionStartDate, ClassSubjectTeacherRelation,AdditionalSubject, AdditionalSubjectTeacherRelation,\
ClassStudentSubjectTeacherRelation, ClassStudentAdditionalSubjectTeacherRelation

#Class model serializer
class ClassNode(DjangoObjectType):
    class Meta:
        model = Class
        filter_fields = []
        interfaces = (relay.Node, )


class AdditionalSubjectNode(DjangoObjectType):
    class Meta:
        model = AdditionalSubject
        filter_fields = []
        interfaces = (relay.Node, )


class ClassDivisionNode(DjangoObjectType):
    class Meta:
        model = ClassDivision
        filter_fields = []
        interfaces = (relay.Node, )

class ClassWhichDivisionNode(DjangoObjectType):
    class Meta:
        model = ClassWhichDivision
        filter_fields = []
        interfaces = (relay.Node, )


class SessionStartDateNode(DjangoObjectType):
    class Meta:
        model = SessionStartDate
        filter_fields = []
        interfaces = (relay.Node, )


class ClassSectionRelationNode(DjangoObjectType):
    class Meta:
        model = ClassSectionRelation
        filter_fields = []
        interfaces = (relay.Node, )


class ClassStudentRelationNode(DjangoObjectType):
    class Meta:
        model = ClassStudentRelation
        filter_fields = []
        interfaces = (relay.Node, )

class ClassSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = ClassSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )


class AdditionalSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = AdditionalSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )


class ClassStudentSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = ClassStudentSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )


class ClassStudentAdditionalSubjectTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = ClassStudentAdditionalSubjectTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )





#Class model QUERY
class Query(graphene.ObjectType):
    classes = relay.Node.Field(ClassNode)
    all_classes = DjangoFilterConnectionField(ClassNode)

    additional_subject = relay.Node.Field(AdditionalSubjectNode)
    all_additional_subject = DjangoFilterConnectionField(AdditionalSubjectNode)

    class_division = relay.Node.Field(ClassDivisionNode)
    all_class_division = DjangoFilterConnectionField(ClassDivisionNode)

    which_division = relay.Node.Field(ClassWhichDivisionNode)
    all_which_division = DjangoFilterConnectionField(ClassWhichDivisionNode)

    class_section = relay.Node.Field(ClassSectionRelationNode)
    all_Class_section = DjangoFilterConnectionField(ClassSectionRelationNode)

    class_section_student = relay.Node.Field(ClassStudentRelationNode)
    all_Class_section_student = DjangoFilterConnectionField(ClassStudentRelationNode)

    session_date = relay.Node.Field(SessionStartDateNode)
    all_session_date = DjangoFilterConnectionField(SessionStartDateNode)

    class_subject_teacher = relay.Node.Field(ClassSubjectTeacherRelationNode)
    all_class_subject_teacher = DjangoFilterConnectionField(ClassSubjectTeacherRelationNode)

    additional_subject_teacher = relay.Node.Field(AdditionalSubjectTeacherRelationNode)
    all_additional_subject_teacher = DjangoFilterConnectionField(AdditionalSubjectTeacherRelationNode)

    student_subject_teacher = relay.Node.Field(ClassStudentSubjectTeacherRelationNode)
    all_student_subject_teacher = DjangoFilterConnectionField(ClassStudentSubjectTeacherRelationNode)

    student_additional_subject_teacher = relay.Node.Field(ClassStudentAdditionalSubjectTeacherRelationNode)
    all_student_additional_subject_teacher = DjangoFilterConnectionField(ClassStudentAdditionalSubjectTeacherRelationNode)





#Class model Mutation resolvers
class ClassDivisionCreationMutation(relay.ClientIDMutation):
    class_division = graphene.Field(ClassDivisionNode)

    class Input:
        duration = graphene.Int(required=True)
        total_divisions = graphene.Int(required=True)
        name = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        if input.get('duration') < 1 or input.get('total_divisions') < 1:
            raise GraphQLError('0 or negitive numbers are not excepted!!')

        else:
            classdivision_obj = ClassDivision.objects.create(
                duration=input.get('duration'),total_divisions=input.get('total_divisions'),name=input.get('name')
                )
            return ClassDivisionCreationMutation(class_division=classdivision_obj)



class SessionDateCreationMutation(relay.ClientIDMutation):
    session_start_date = graphene.Field(SessionStartDateNode)

    class Input:
        year = graphene.Int(required=True)
        month = graphene.Int(required=True)
        date = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if input.get('year') < 2010 or input.get('month') < 1 or input.get('month') > 12 or input.get('date') < 1 or input.get('date') > 31:
            raise GraphQLError('please enter a valide Date!!')

        else:
            date = datetime.date(input.get('year'),input.get('month'),input.get('date'))
            session_date_obj = SessionStartDate.objects.create(start_date=date)

            return SessionDateCreationMutation(session_start_date=session_date_obj)


class ClassMutation(relay.ClientIDMutation):
    Class_node = graphene.Field(ClassNode)

    class Input:
        class_id = graphene.ID(required=True)
        alias = graphene.String()
        department = graphene.ID()
        class_teacher = graphene.ID()
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        if input.get('mutation_option') not in (2,3):
            raise GraphQLError('Enter valide mutation option')

        else:
            try:
                class_obj = Class.objects.select_related('department','institution').get(id=from_global_id(input.get('class_id'))[1])
            except Class.DoesNotExist:
                raise GraphQLError('class ID is incorrect!!')
            result = UserAuthorizeTest(info,'classTeacher','hod',department_obj=class_obj.department,class_obj=class_obj)

            if result['classTeacher'] or result['hod']:
                if input.get('department') is not None:
                    try:
                        department_obj = Department.objects.get(id=from_global_id(input.get('department'))[1])
                    except Department.DoesNotExist:
                        raise GraphQLError('Department ID is incorrect!!')

                if input.get('class_teacher') is not None:
                    try:
                        teacher_obj = InstitutionTeacherRelation.objects.select_related('institution').get(
                            id=from_global_id(input.get('class_teacher'))[1]
                            )
                    except InstitutionTeacherRelation.DoesNotExist:
                        raise GraphQLError('Teacher ID is incorrect!!')
                    if class_obj.institution != teacher_obj.institution:
                        raise GraphQLError('teacher and class does not belong to the same institution')

                if input.get('mutation_option') == 2:
                    if input.get('alias') is not None:
                        class_obj.alias = input.get('alias')

                    if input.get('department') is not None:
                        class_obj.department = department_obj

                    if input.get('class_teacher') is not None:
                        class_obj.teacher = teacher_obj

                    class_obj.save()
                    return ClassMutation(Class_node=class_obj)

                else:
                    class_obj.delete()
                    return ClassMutation(Class_node=None)

            else:
                raise GraphQLError('you don\'t have proper permission. try different account')


class AdditionalSubjectMutation(relay.ClientIDMutation):
    additional_subject = graphene.Field(AdditionalSubjectNode)

    class Input:
        additional_subject_id = graphene.ID()
        class_id = graphene.ID()
        subject_id = graphene.ID()
        subject_type = graphene.String()
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):

        if input.get('mutation_option') not in (2,3):
            raise GraphQLError('Enter valide mutation option')

        else:
            if input.get('mutation_option') == 2:
                if input.get('class_id') is not None or input.get('subject_id') is not None:
                    try:
                        class_obj = Class.objects.select_related('department').get(id=from_global_id(input.get('class_id'))[1])
                    except Class.DoesNotExist:
                        raise GraphQLError('class ID is incorrect!!')

                    result = UserAuthorizeTest(info,'classTeacher','hod',department_obj=class_obj.department,class_obj=class_obj)

                    if result['classTeacher'] or result['hod']:
                        try:
                            subject_obj = Subject.objects.get(id=from_global_id(input.get('subject_id'))[1])
                        except Subject.DoesNotExist:
                            raise GraphQLError('subject ID is incorrect!!')


                        if input.get('subject_type') is not None:
                            valide_choice = False

                            for choice in AdditionalSubject.SUBJECT_TYPE:
                                if input.get('subject_type') == choice[0]:
                                    valide_choice = True
                                    break

                            if valide_choice is False:
                                raise GraphQLError('provie valide subject label value')

                            additional_subject_obj, created = AdditionalSubject.objects.get_or_create(
                                Class=class_obj, subject=subject_obj, subject_type=input.get('subject_type')
                                )
                        else:
                            additional_subject_obj, created = AdditionalSubject.objects.get_or_create(
                                Class=class_obj, subject=subject_obj
                                )

                        return AdditionalSubjectMutation(additional_subject=additional_subject_obj)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('Provide Class and Subject ID for adding new additional subject to class.')

            else:
                if input.get('additional_subject_id') is not None:
                    try:
                        additional_subject_obj = AdditionalSubject.objects.select_related('Class__department').get(
                            id=from_global_id(input.get('additional_subject_id'))[1]
                            )
                    except AdditionalSubject.DoesNotExist:
                        raise GraphQLError('Additional Subject ID is incorrect!!')

                    class_obj = additional_subject_obj.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )

                    if result['classTeacher'] or result['hod']:
                        additional_subject_obj.delete()
                        return AdditionalSubjectMutation(additional_subject=None)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('Provide Class additional subject ID for deleting.')





class ClassSectionMutation(relay.ClientIDMutation):
    class_section = graphene.Field(ClassSectionRelationNode)

    class Input:
        which_division_id = graphene.ID()
        section = graphene.String()
        section_teacher_id = graphene.ID()
        class_section_id = graphene.ID()
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if input.get('mutation_option') not in (1,2,3):
            raise GraphQLError('Enter valide mutation option')

        else:
            if input.get('mutation_option') == 1:
                if input.get('which_division_id') is not None or input.get('section')  is not None:
                    try:
                        which_division_obj = ClassWhichDivision.objects.select_related('Class__department','no_section').get(
                            id=from_global_id(input.get('which_division_id'))[1]
                            )
                    except ClassWhichDivision.DoesNotExist:
                        raise GraphQLError('Which division ID is incorrect')

                    if which_division_obj.no_section:
                        raise GraphQLError('You can\'t create any sections for this class' )

                    class_obj = which_division_obj.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )

                    if result['classTeacher'] or result['hod']:
                        if ClassSectionRelation.objects.filter(which_division=which_division_obj,section=input.get('section')).exists():
                            raise GraphQLError('this class section already exists. please provide unique entry.')

                        class_section_obj = ClassSectionRelation(
                            which_division=which_division_obj,section=input.get('section')
                            )

                        if input.get('section_teacher_id') is not None:
                            try:
                                teacher_obj = InstitutionTeacherRelation.objects.select_related('institution').get(
                                    id=from_global_id(input.get('section_teacher_id'))[1]
                                    )
                            except InstitutionTeacherRelation.DoesNotExist:
                                raise GraphQLError('Teacher ID is incorrect!!')

                            if class_obj.institution != teacher_obj.institution:
                                raise GraphQLError('teacher and class section does not belong to the same institution')

                            class_section_obj.teacher = teacher_obj
                            class_section_obj.save()
                        else:
                            class_section_obj.save()

                        return ClassSectionMutation(class_section=class_section_obj)

                else:
                    raise GraphQLError('provide approprate information to create class section')

            elif input.get('mutation_option') == 2:
                if input.get('class_section_id') is not None or input.get('section_teacher_id')  is not None:
                    try:
                        class_section_obj = ClassSectionRelation.objects.select_related('which_division__Class__department').get(
                            id=from_global_id(input.get('class_section_id'))[1]
                            )
                    except ClassSectionRelation.DoesNotExist:
                        raise GraphQLError('Class section ID is incorrect')

                    class_obj = class_section_obj.which_division.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )
                    if result['classTeacher'] or result['hod']:
                        try:
                            teacher_obj = InstitutionTeacherRelation.objects.select_related('institution').get(
                                id=from_global_id(input.get('section_teacher_id'))[1]
                                )
                        except InstitutionTeacherRelation.DoesNotExist:
                            raise GraphQLError('Teacher ID is incorrect!!')
                        if class_obj.institution != teacher_obj.institution:
                            raise GraphQLError('teacher and class section does not belong to the same institution')

                        class_section_obj.teacher = teacher_obj
                        class_section_obj.save()

                        return ClassSectionMutation(class_section=class_section_obj)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('provide approprate information to update class section')

            else:
                if input.get('class_section_id') is not None:
                    try:
                        class_section_obj = ClassSectionRelation.objects.select_related('which_division__Class__department').get(
                            id=from_global_id(input.get('class_section_id'))[1]
                            )
                    except ClassSectionRelation.DoesNotExist:
                        raise GraphQLError('Class section ID is incorrect')

                    if class_section_obj.which_division.no_section:
                        raise GraphQLError('you can\'t delete this section.')

                    class_obj = class_section_obj.which_division.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )
                    if result['classTeacher'] or result['hod']:
                        class_section_obj.delete()
                        return ClassSectionMutation(class_section=None)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('provide approprate information to update class section')

                    


class ClassSectionStudentMutation(relay.ClientIDMutation):
    class_section_student = graphene.Field(ClassStudentRelationNode)

    class Input:
        section_student_id = graphene.ID()
        student_id = graphene.ID()
        class_section_id = graphene.ID()
        session_date_id = graphene.ID()
        section_subject_teacher = graphene.String()
        additional_subject_teacher = graphene.String()
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        #checking for appropriate options
        if input.get('mutation_option') not in (1,2,3):
            raise GraphQLError('Enter valide mutation option')

        else:
            #create option
            if input.get('mutation_option') == 1:
                #checking presence of all required values
                if input.get('student_id') is not None or input.get('class_section_id') is not None or input.get('session_date_id') is not None:
                    #retriving instance of class_section_relation
                    try:
                        class_section_obj = ClassSectionRelation.objects.select_related('which_division__Class__department').get(
                            id=from_global_id(input.get('class_section_id'))[1]
                            )
                    except ClassSectionRelation.DoesNotExist:
                        raise GraphQLError('class section ID does not exist')

                    #saving class_object
                    class_obj = class_section_obj.which_division.Class

                    #checking for proper permissions
                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )
                    #when permissions checked
                    if result['classTeacher'] or result['hod']:
                        #retriving instance of institution_student_relation
                        try:
                            student_obj = InstitutionStudentRelation.objects.select_related('institution').get(
                                id=from_global_id(input.get('student_id'))[1]
                                )
                        except InstitutionStudentRelation.DoesNotExist:
                            raise GraphQLError('student ID does not exist')

                        #checking weather student and class belongs to the same institution or not 
                        if student_obj.institution != class_obj.institution:
                            raise GraphQLError('student and class section does not belong to the same institution')

                        #checking weather instance of student and class_section already exists in DB
                        if ClassStudentRelation.objects.filter(student=student_obj).exists():
                            raise GraphQLError('student is already belongs to a class section. provide unique student entry')

                        #retriving instacne of session_date
                        try:
                            session_date_obj = SessionStartDate.objects.get(id=from_global_id(input.get('session_date_id'))[1])
                        except SessionStartDate.DoesNotExist:
                            raise GraphQLError('session date ID does not exist')

                        #creating class_section_relation instance in DB
                        section_student_obj = ClassStudentRelation(
                            student=student_obj,section=class_section_obj,session_start_date=session_date_obj
                            )

                        if input.get('section_subject_teacher') is not None:
                            json_string = input.get('section_subject_teacher')
                            json_data = json.loads(json_string)

                            for section_subject_teacher in json_data['section_subject_teacher']:
                                section_teacher_exists = ClassSubjectTeacherRelation.objects.filter(
                                    id=from_global_id(section_subject_teacher)[1],teacher__institution=student_obj.institution
                                    ).exists()
                                if section_teacher_exists is not True:
                                    raise GraphQLError('subject teacher doesn\'t not exist in the given institution')

                            section_student_obj._subject_teacher = json_data['section_subject_teacher']

                        if input.get('additional_subject_teacher') is not None:
                            json_string = input.get('additional_subject_teacher')
                            json_data = json.loads(json_string)

                            for additional_subject_teacher in json_data['additional_subject_teacher']:
                                add_sub_teach_exist = AdditionalSubjectTeacherRelation.objects.filter(
                                    id=from_global_id(additional_subject_teacher)[1],teacher__institution=student_obj.institution
                                    ).exists()
                                if add_sub_teach_exist is not True:
                                    raise GraphQLError('additional subject teacher doesn\'t not exist in the given institution')

                            section_student_obj._additional_subject_teacher = json_data['additional_subject_teacher']

                        section_student_obj.save()

                        return ClassSectionStudentMutation(class_section_student=section_student_obj)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('provide approprate information to create section student relation')




            elif input.get('mutation_option') == 2:
                if input.get('section_student_id') is not None or input.get('class_section_id') is not None:
                    try:
                        section_student_obj = ClassStudentRelation.objects.select_related(
                            'student','section__which_division__Class__department','session_start_date'
                            ).get(id=from_global_id(input.get('section_student_id'))[1])
                    except ClassStudentRelation.DoesNotExist:
                        raise GraphQLError('section student ID doesn\'t exist')

                    class_obj = section_student_obj.section.which_division.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )

                    if result['classTeacher'] or result['hod']:
                        try:
                            class_section_obj = ClassSectionRelation.objects.select_related('which_division__Class__institution').get(
                                id=from_global_id(input.get('class_section_id'))[1]
                                )
                        except ClassSectionRelation.DoesNotExist:
                            raise GraphQLError('class section ID does not exist')

                        if class_obj.institution != class_section_obj.which_division.Class.institution:
                            raise GraphQLError('student and class section doesn\'t belong to the same institution')

                        if class_section_obj == section_student_obj.section:
                            raise GraphQLError('provide a new section to update the student section')
                        
                        new_section_student_obj = ClassStudentRelation(
                            student=section_student_obj.student,section=class_section_obj,
                            session_start_date=section_student_obj.session_start_date
                            )
                        section_student_obj.delete()

                        if input.get('section_subject_teacher') is not None:
                            json_string = input.get('section_subject_teacher')
                            json_data = json.loads(json_string)

                            new_section_student_obj._subject_teacher = json_data['section_subject_teacher']

                            for section_subject_teacher in json_data['section_subject_teacher']:
                                section_teacher_exists = ClassSubjectTeacherRelation.objects.filter(
                                    id=from_global_id(section_subject_teacher)[1],teacher__institution=new_section_student_obj.student.institution
                                    ).exists()
                                if section_teacher_exists is not True:
                                    raise GraphQLError('subject teacher doesn\'t not exist in the given institution')


                        if input.get('additional_subject_teacher') is not None:
                            json_string = input.get('additional_subject_teacher')
                            json_data = json.loads(json_string)

                            new_section_student_obj._additional_subject_teacher = json_data['additional_subject_teacher']

                            for additional_subject_teacher in json_data['additional_subject_teacher']:
                                add_sub_teach_exist = AdditionalSubjectTeacherRelation.objects.filter(
                                    id=from_global_id(additional_subject_teacher)[1],teacher__institution=new_section_student_obj.student.institution
                                    ).exists()
                                if add_sub_teach_exist is not True:
                                    raise GraphQLError('additional subject teacher doesn\'t not exist in the given institution')

                        new_section_student_obj.save()

                        return ClassSectionStudentMutation(class_section_student=new_section_student_obj)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('provide approprate information to update section student relation')



            else:
                if input.get('section_student_id') is not None:
                    try:
                        section_student_obj = ClassStudentRelation.objects.select_related(
                            'section__which_division__Class__department'
                            ).get(id=from_global_id(input.get('section_student_id'))[1])
                    except ClassStudentRelation.DoesNotExist:
                        raise GraphQLError('section student ID doesn\'t exist')

                    class_obj = section_student_obj.section.which_division.Class

                    result = UserAuthorizeTest(
                        info,'classTeacher','hod',department_obj=class_obj.department,
                        class_obj=class_obj
                        )

                    if result['classTeacher'] or result['hod']:
                        section_student_obj.delete()
                        return ClassSectionStudentMutation(class_section_student=None)

                    else:
                        raise GraphQLError('you don\'t have proper permission. try different account')

                else:
                    raise GraphQLError('provide approprate information to delete section student relation')




class SubjectTeacherMutation(relay.ClientIDMutation):
    class_subject_teacher = graphene.Field(ClassSubjectTeacherRelationNode)
    class_additional_subject_teacher = graphene.Field(AdditionalSubjectTeacherRelationNode)

    class Input:
        teacher_id = graphene.String()
        section_id = graphene.String()
        subject_id = graphene.String()
        subject_teacher_id = graphene.String()
        additional_or_subject_teacher = graphene.Int(required=True)
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if input.get('additional_or_subject_teacher') not in (1,2):
            raise GraphQLError('enter proper vlues')

        else:
            if input.get('mutation_option') not in (1,2,3):
                raise GraphQLError('please enter proper values')

            else:
                if input.get('mutation_option') == 1:
                    if input.get('teacher_id') is None or input.get('section_id') is None or input.get('subject_id') is None:
                        raise GraphQLError('please prove full required values')

                    else:
                        try:
                            section_obj = ClassSectionRelation.objects.select_related('which_division__Class__department').get(
                                id=from_global_id(input.get('section_id'))[1]
                                )
                        except ClassSectionRelation.DoesNotExist:
                            raise GraphQLError('section ID is incorrect')

                        class_obj = section_obj.which_division.Class

                        result = UserAuthorizeTest(
                            info,'classTeacher','hod',department_obj=class_obj.department,
                            class_obj=class_obj
                            )

                        if result['classTeacher'] or result['hod']:
                            if InstitutionTeacherRelation.objects.filter(id=from_global_id(input.get('teacher_id'))[1],institution=class_obj.institution).exists() is not True:
                                raise GraphQLError('teacher ID is incorrect or does not belong to same institution')

                            if input.get('additional_or_subject_teacher') is 1:
                                if CourseSubjectRelation.objects.filter(id=from_global_id(input.get('subject_id'))[1],course=class_obj.course).exists() is not True:
                                    raise GraphQLError('subject ID is incorrect or does not belong to same course')

                            if input.get('additional_or_subject_teacher') is 2:
                                if AdditionalSubject.objects.filter(id=from_global_id(input.get('subject_id'))[1],Class=class_obj).exists() is not True:
                                    raise GraphQLError('subject ID is incorrect or does not belong to same class')

                            teacher_obj = InstitutionTeacherRelation.objects.get(id=from_global_id(input.get('teacher_id'))[1])

                            if input.get('additional_or_subject_teacher') is 1:
                                subject_obj = CourseSubjectRelation.objects.get(id=from_global_id(input.get('subject_id'))[1])
                                subject_teacher_obj = ClassSubjectTeacherRelation(subject=subject_obj)

                            if input.get('additional_or_subject_teacher') is 2:
                                subject_obj = AdditionalSubject.objects.get(id=from_global_id(input.get('subject_id'))[1])
                                subject_teacher_obj = AdditionalSubjectTeacherRelation(subject=subject_obj)

                            subject_teacher_obj.teacher = teacher_obj
                            subject_teacher_obj.section = section_obj
                            try:
                                subject_teacher_obj.save()
                            except IntegrityError:
                                raise GraphQLError('subject teacher already exists in the system')

                            if input.get('additional_or_subject_teacher') is 1:
                                return SubjectTeacherMutation(class_subject_teacher=subject_teacher_obj)

                            if input.get('additional_or_subject_teacher') is 2:
                                return SubjectTeacherMutation(class_additional_subject_teacher=subject_teacher_obj)

                        else:
                            raise GraphQLError('you don\'t have proper permission. Try different account')


                if input.get('mutation_option') == 2:
                    if input.get('teacher_id') is None or input.get('subject_teacher_id') is None:
                        raise GraphQLError('please provide full required values')

                    if input.get('additional_or_subject_teacher') not in (1,2):
                        raise GraphQLError('please provide approprate value')

                    else:
                        if input.get('additional_or_subject_teacher') is 1:
                            try:
                                subject_teacher_obj = ClassSubjectTeacherRelation.objects.select_related('section__which_division__Class__department').get(
                                    id=from_global_id(input.get('subject_teacher_id'))[1]
                                    )
                            except ClassSubjectTeacherRelation.DoesNotExist:
                                raise GraphQLError('subejct teacher ID is incorrect')

                        if input.get('additional_or_subject_teacher') is 2:
                            try:
                                subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.select_related('section__which_division__Class__department').get(
                                    id=from_global_id(input.get('subject_teacher_id'))[1]
                                    )
                            except AdditionalSubjectTeacherRelation.DoesNotExist:
                                raise GraphQLError('additional subejct teacher ID is incorrect')

                        class_obj = subject_teacher_obj.section.which_division.Class

                        result = UserAuthorizeTest(
                            info,'classTeacher','hod',department_obj=class_obj.department,
                            class_obj=class_obj
                            )

                        if result['classTeacher'] or result['hod']:
                            if InstitutionTeacherRelation.objects.filter(id=from_global_id(input.get('teacher_id'))[1],institution=class_obj.institution).exists() is not True:
                                raise GraphQLError('teacher ID is incorrect or does not belong to same institution')

                            teacher_obj = InstitutionTeacherRelation.objects.get(id=from_global_id(input.get('teacher_id'))[1])

                            subject_teacher_obj.teacher = teacher_obj

                            subject_teacher_obj.save()

                            if input.get('additional_or_subject_teacher') is 1:
                                return SubjectTeacherMutation(class_subject_teacher=subject_teacher_obj)

                            if input.get('additional_or_subject_teacher') is 2:
                                return SubjectTeacherMutation(class_additional_subject_teacher=subject_teacher_obj)

                        else:
                            raise GraphQLError('you don\'t have proper permission. Try different account')


                else:
                    if input.get('subject_teacher_id') is None:
                        raise GraphQLError('provide proper value')

                    if input.get('additional_or_subject_teacher') not in (1,2):
                        raise GraphQLError('please provide approprate value')

                    else:
                        if input.get('additional_or_subject_teacher') is 1:
                            try:
                                subject_teacher_obj = ClassSubjectTeacherRelation.objects.select_related('section__which_division__Class__department').get(
                                    id=from_global_id(input.get('subject_teacher_id'))[1]
                                    )
                            except ClassSubjectTeacherRelation.DoesNotExist:
                                raise GraphQLError('subejct teacher ID is incorrect')

                        if input.get('additional_or_subject_teacher') is 2:
                            try:
                                subject_teacher_obj = AdditionalSubjectTeacherRelation.objects.select_related('section__which_division__Class__department').get(
                                    id=from_global_id(input.get('subject_teacher_id'))[1]
                                    )
                            except AdditionalSubjectTeacherRelation.DoesNotExist:
                                raise GraphQLError('additional subejct teacher ID is incorrect')

                        class_obj = subject_teacher_obj.section.which_division.Class

                        result = UserAuthorizeTest(
                            info,'classTeacher','hod',department_obj=class_obj.department,
                            class_obj=class_obj
                            )

                        if result['classTeacher'] or result['hod']:
                            subject_teacher_obj.delete()

                            if input.get('additional_or_subject_teacher') is 1:
                                return SubjectTeacherMutation(class_subject_teacher=None)

                            if input.get('additional_or_subject_teacher') is 2:
                                return SubjectTeacherMutation(class_additional_subject_teacher=None)

                        else:
                            raise GraphQLError('you don\'t have proper permission. Try different account')


class Mutation(graphene.ObjectType):
    class_division = ClassDivisionCreationMutation.Field()
    session_start_date = SessionDateCreationMutation.Field()
    class_update_delete = ClassMutation.Field()
    class_additional_subject = AdditionalSubjectMutation.Field()
    class_section = ClassSectionMutation.Field()
    class_section_student = ClassSectionStudentMutation.Field()
    class_subject_teacher = SubjectTeacherMutation.Field()
import json

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from account.permissions import UserAuthorizeTest

from account.models import User
from .models import Institution, InstitutionTeacherRelation, InstitutionStudentRelation, AuthorityRole, SuperAdminControl
from course.models import Course, Subject, CourseSubjectRelation
from userInvite.models import UserInvite

from Class.models import Class, AdditionalSubject, ClassDivision, ClassSectionRelation,\
 ClassWhichDivision, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation,\
 ClassStudentRelation, SessionStartDate, ClassStudentSubjectTeacherRelation, ClassStudentAdditionalSubjectTeacherRelation

from department.models import Department
from teacherProfile.models import TeacherRegistrationNumber
from studentProfile.models import StudentRegistrationNumber


class SuperAdminControlNode(DjangoObjectType):
    class Meta:
        model = SuperAdminControl
        filter_fields = []
        interfaces = (relay.Node, )

class InstitutionNode(DjangoObjectType):
    class Meta:
        model = Institution
        filter_fields = []
        interfaces = (relay.Node, )

class InstitutionTeacherRelationNode(DjangoObjectType):
    class Meta:
        model = InstitutionTeacherRelation
        filter_fields = []
        interfaces = (relay.Node, )

class InstitutionStudentRelationNode(DjangoObjectType):
    class Meta:
        model = InstitutionStudentRelation
        filter_fields = []
        interfaces = (relay.Node, )

class AuthorityRoleNode(DjangoObjectType):
    class Meta:
        model = AuthorityRole
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    super_admin_control = relay.Node.Field(SuperAdminControlNode)
    all_super_admin_control = DjangoFilterConnectionField(SuperAdminControlNode)

    institution = relay.Node.Field(InstitutionNode)
    all_institution = DjangoFilterConnectionField(InstitutionNode)

    institution_teacher_relation = relay.Node.Field(InstitutionTeacherRelationNode)
    all_institution_teacher_relation = DjangoFilterConnectionField(InstitutionTeacherRelationNode)

    institution_student_relation = relay.Node.Field(InstitutionStudentRelationNode)
    all_institution_student_relation = DjangoFilterConnectionField(InstitutionStudentRelationNode)

    authorityRole = relay.Node.Field(AuthorityRoleNode)
    all_authorityRole = DjangoFilterConnectionField(AuthorityRoleNode)


class InitialClassMutation(relay.ClientIDMutation):
    institution = graphene.Field(InstitutionNode)

    class Input:
        institution_id = graphene.ID(required=True)
        class_json = graphene.String(required=True) # json string data


    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            institution_obj = Institution.objects.get(id=from_global_id(input.get('institution_id'))[1])
        except Institution.DoesNotExist:
            raise GraphQLError('institution ID is incorrect')

        result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)
        if result['adminUser']:
            json_string = input.get('class_json')
            json_data = json.loads(json_string)

            for i in json_data["class"]:
                if Course.objects.filter(id=from_global_id(i["course_id"])[1]).exists():
                    raise GraphQLError('course ID is incorrect')

                if ClassDivision.objects.get(id=from_global_id(i["class_division_id"])[1]).exists():
                    raise GraphQLError('class division ID is incorrect')

            for i in json_data["class"]:
                course_instance = Course.objects.get(id=from_global_id(i["course_id"])[1])
                class_division_instance = ClassDivision.objects.get(id=from_global_id(i["class_division_id"])[1])
                class_creation = Class(institution=institution_obj, course=course_instance, division=class_division_instance)
                if "class_alias" in i:
                    class_creation.alias = i["class_alias"]
                class_creation.save()

                if "additional_subject" in i:
                    for addon_subject in i["additional_subject"]:
                        if Subject.objects.get(id=from_global_id(addon_subject['subject_id'])[1]).exists():
                            raise GraphQLError('subject ID is incorrect')

                        valide_choice = False

                        for choice in AdditionalSubject.SUBJECT_TYPE:
                            if addon_subject['subject_type'] == choice[0]:
                                valide_choice = True
                                break

                        if valide_choice is False:
                            raise GraphQLError('provie valide subject label value')

                    for addon_subject in i["additional_subject"]:
                        subject = Subject.objects.get(id=from_global_id(addon_subject['subject_id'])[1])
                        AdditionalSubject.objects.create(Class=class_creation, subject=subject, subject_type=addon_subject['subject_type'])

        return InitialClassMutation(institution=institution_obj)



class InitialDepartmentSectionMutation(relay.ClientIDMutation):
    institution = graphene.Field(InstitutionNode)

    class Input:
        institution_id = graphene.ID(required=True)
        departmentSection_json = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            institution_obj = Institution.objects.get(id=from_global_id(input.get('institution_id'))[1])
        except Institution.DoesNotExist:
            raise GraphQLError('institution ID is incorrect')

        result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)
        if result['adminUser']:
            json_string = input.get('departmentSection_json')
            json_data = json.loads(json_string)

            for department in json_data["department_class"]:
                department_name_exists = False

                if "department_name" in department:
                    department_name_exists = True
                    department_obj = Department.objects.create(name=department["department_name"], institution=institution_obj)

                for classArray in department["class"]:
                    class_id = Class.objects.filter(id=from_global_id(classArray["class_id"])[1],institution=institution_obj).exists()
                    if class_id is not True:
                        raise GraphQLError('class ID is incorrect or does not belong to same instiution.')

                for classArray in department["class"]:
                    class_obj = Class.objects.get(id=from_global_id(classArray["class_id"])[1])
                    class_division_obj = class_obj.division
                    
                    if department_name_exists:
                        class_obj.department = department_obj
                        class_obj.save()

                    for division_section in classArray["classDivision_section"]:
                        if division_section["division_number"] <= class_division_obj.total_divisions:
                            class_which_division_obj = ClassWhichDivision.objects.create(
                                Class=class_obj, 
                                which_division=division_section["division_number"], no_section=division_section["division_no_section"]
                                )
                            if class_which_division_obj.no_section:
                                ClassSectionRelation.objects.create(which_division=class_which_division_obj)

                            else:
                                if "section" in division_section:
                                    for section in division_section["section"]:
                                        ClassSectionRelation.objects.create(which_division=class_which_division_obj, section=section)
                        else:
                            raise GraphQLError('class division number is out of bound with total division')

        return InitialDepartmentSectionMutation(institution=institution_obj)




class InviteSend(relay.ClientIDMutation):
    institution = graphene.Field(InstitutionNode)

    class Input:
        institution_id = graphene.ID(required=True)
        inviteUser_json = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            institution_obj = Institution.objects.get(id=from_global_id(input.get('institution_id'))[1])
        except Institution.DoesNotExist:
            raise GraphQLError('institution ID is incorrect')

        result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)
        if result['adminUser']:
            json_string = input.get('inviteUser_json')
            json_data = json.loads(json_string)

            if "teacher" in json_data:
                for teacher in json_data["teacher"]:
                    UserInvite.objects.create(
                        institution=institution_obj, email=teacher["email"], register_number=teacher["register_number"],
                        profile_type="teach", invite_status="send"
                        )
            if "student" in json_data:
                for student in json_data["student"]:
                    UserInvite.objects.create(
                        institution=institution_obj, email=student["email"], register_number=student["register_number"],
                        profile_type="stu", invite_status="send"
                        )
            return InviteSend(institution=institution_obj)
                    



class InitialTeacherSignupMutation(relay.ClientIDMutation):
    institution = graphene.Field(InstitutionNode)

    class Input:
        institution_id = graphene.ID(required=True)
        teacherList_json = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            institution_obj = Institution.objects.get(id=from_global_id(input.get('institution_id'))[1])
        except Institution.DoesNotExist:
            raise GraphQLError('institution ID is incorrect')

        result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)
        if result['adminUser']:
            json_string = input.get('teacherList_json')
            json_data = json.loads(json_string)

            for teacher in json_data["teacher"]:
                signup = teacher["signup"]
                user = User(
                    email=signup["email"], first_name=signup["first_name"], last_name=signup["last_name"], is_active=False
                    )
                user.set_unusable_password()
                user._teacher_profile = True      
                user.save()

                teacherprofile = user.nxtgenuser.teacherprofile
                TeacherRegistrationNumber.objects.create(
                    teacher=teacherprofile, institution=institution_obj, registration_number=signup["register_number"]
                    )

                try:
                    authority_role = AuthorityRole.objects.get(id=from_global_id(signup["authority_role"])[1])
                except AuthorityRole.DoesNotExist:
                    raise GraphQLError('authority ID is incorrect')

                institution_teacher_relation = InstitutionTeacherRelation.objects.create(
                    institution=institution_obj, teacher=teacherprofile,
                    authority_role=authority_role
                    )

                if "positions" in teacher:
                    positions = teacher["positions"]

                    if "department" in positions:
                        if Department.objects.filter(id=from_global_id(positions["department"])[1],institution=institution_obj).exists() is not True:
                            raise GraphQLError('department ID is incorrect or does not belong to same institution')

                    if "class" in positions:
                        if Class.objects.filter(id=from_global_id(positions["class"])[1],institution=institution_obj).exists() is not True:
                            raise GraphQLError('class ID is incorrect or does not belong to same institution')

                    if "class_section" in positions:
                        if ClassSectionRelation.objects.filter(id=from_global_id(positions["class_section"])[1],which_division__Class__institution=institution_obj).exists() is not True:
                            raise GraphQLError('class section ID is incorrect or does not belong to same institution')


                if "class_subject" in teacher:
                    for class_subject in teacher["class_subject"]:
                        subject = CourseSubjectRelation.objects.filter(id=from_global_id(class_subject["course_subject"])[1]).exists()

                        if subject is not True:
                            raise GraphQLError('subject ID is incorrect')

                        for class_section in class_subject["section"]:
                            section = ClassSectionRelation.objects.filter(
                                id=from_global_id(class_section)[1],which_division__Class__institution=institution_obj
                                ).exists()
                            if section is not True:
                                raise GraphQLError('class section ID is incorrect or does not belong to the same institution')
                            
                if "class_additional_subject" in teacher:
                    for class_additional_subject in teacher["class_additional_subject"]:
                        addon_subject = AdditionalSubject.objects.filter(
                            id=from_global_id(class_additional_subject["addition_subject"])[1],Class__institution=institution_obj
                            ).exists()

                        if addon_subject is not True:
                            raise GraphQLError('addition subject teacher ID is incorrect or does not belong to the same institution')

                        for class_section in class_additional_subject["section"]:
                            section = ClassSectionRelation.objects.filter(
                                id=from_global_id(class_section)[1],which_division__Class__institution=institution_obj
                                ).exists()
                            if section is not True:
                                raise GraphQLError('class section ID is incorrect or does not belong to the same institution')



                if "positions" in teacher:
                    positions = teacher["positions"]

                    if "department" in positions:
                        department = Department.objects.get(id=from_global_id(positions["department"])[1])
                        department.hod = institution_teacher_relation
                        department.save()

                    if "class" in positions:
                        Class = Class.objects.get(id=from_global_id(positions["class"])[1])
                        Class.teacher = institution_teacher_relation
                        Class.save()

                    if "class_section" in positions:
                        class_section = ClassSectionRelation.objects.get(id=from_global_id(positions["class_section"])[1])
                        class_section.teacher = institution_teacher_relation
                        class_section.save()

                if "class_subject" in teacher:
                    for class_subject in teacher["class_subject"]:
                        subject = CourseSubjectRelation.objects.get(id=from_global_id(class_subject["course_subject"])[1])
                        for class_section in class_subject["section"]:
                            section = ClassSectionRelation.objects.get(id=from_global_id(class_section)[1])
                            ClassSubjectTeacherRelation.objects.create(
                                subject=subject, teacher=institution_teacher_relation, section=section
                                )
                if "class_additional_subject" in teacher:
                    for class_additional_subject in teacher["class_additional_subject"]:
                        addon_subject = AdditionalSubject.objects.get(id=from_global_id(class_additional_subject["addition_subject"])[1])
                        for class_section in class_additional_subject["section"]:
                            section = ClassSectionRelation.objects.get(id=from_global_id(class_section)[1])
                            AdditionalSubjectTeacherRelation.objects.create(
                                    subject=addon_subject, teacher=institution_teacher_relation, section=section
                                )

        return InitialTeacherSignupMutation(institution=institution_obj)


class InitialStudentSignupMutation(relay.ClientIDMutation):
    institution = graphene.Field(InstitutionNode)

    class Input:
        institution_id = graphene.ID(required=True)
        studentList_json = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            institution_obj = Institution.objects.get(id=from_global_id(input.get('institution_id'))[1])
        except Institution.DoesNotExist:
            raise GraphQLError('institution ID is incorrect')

        result = UserAuthorizeTest(info,'adminUser',institution_obj=institution_obj)
        if result['adminUser']:
            json_string = input.get('studentList_json')
            json_data = json.loads(json_string)

            for student in json_data["student"]:
                class_section = ClassSectionRelation.objects.filter(
                    id=from_global_id(student["section"])[1],which_division__Class__institution=institution_obj
                    ).exists()

                if class_section:
                    class_section_obj = ClassSectionRelation.objects.get(id=from_global_id(student["section"])[1])

                else:
                    raise GraphQLError('Either class section ID is incorrect or it does not belong to the same institution')

                try:
                    session_start_date = SessionStartDate.objects.get(id=from_global_id(student["session"])[1])
                except SessionStartDate.DoesNotExist:
                    raise GraphQLError('session date ID is incorrect')
                

                for signup in student["signup"]:
                    user = User(
                        email=signup["email"], first_name=signup["first_name"], last_name=signup["last_name"], is_active=False
                        )
                    user.set_unusable_password()
                    user._student_profile = True    
                    user.save()

                    studentprofile = user.nxtgenuser.studentprofile
                    StudentRegistrationNumber.objects.create(
                            student=studentprofile, institution=institution_obj, registration_number=signup["register_number"]
                        )
                    institution_student_relation = InstitutionStudentRelation.objects.create(
                        institution=institution_obj, student=studentprofile
                        )
                    student_section = ClassStudentRelation(
                        student=institution_student_relation, section=class_section_obj, session_start_date=session_start_date
                        )

                    subject_teacher_ids = []
                    additional_subject_teacher_ids = []

                    if "section_subject_teacher" in student:
                        global_subject_teacher = student["section_subject_teacher"]

                        for subject_teacher in global_subject_teacher:
                            section_subject_teacher = ClassSubjectTeacherRelation.objects.filter(
                                id=from_global_id(subject_teacher)[1],teacher__institution=institution_obj
                                ).exists()

                            if section_subject_teacher is not True:
                                raise GraphQLError('subject teacher ID is incorrect or does not exist in the same institution')

                        subject_teacher_ids.extend(global_subject_teacher)


                    if "additional_subject_teacher" in student:
                        global_additional_subject_teacher = student["additional_subject_teacher"]

                        for additional_subject_teacher in global_additional_subject_teacher:
                            section_addon_subject_teacher = AdditionalSubjectTeacherRelation.objects.filter(
                                id=from_global_id(additional_subject_teacher)[1],teacher__institution=institution_obj
                                ).exists()

                            if section_addon_subject_teacher is not True:
                                raise GraphQLError('additional subject teacher ID is incorrect or does not belong to same institution')
                            

                        additional_subject_teacher_ids.extend(global_additional_subject_teacher)

                    if "section_subject_teacher" in signup:
                        for custom_subject in signup["section_subject_teacher"]:
                            subject_teacher = ClassSubjectTeacherRelation.objects.filter(
                                id=from_global_id(custom_subject["section_subject_teacher"])[1],teacher__institution=institution_obj
                                ).exists()

                            if subject_teacher is not None:
                                raise GraphQLError('subject teacher ID is incorrect or does not exist in the same institution')
                            

                        subject_teacher_ids.extend(signup["section_subject_teacher"])

                    if "additional_subject_teacher" in signup:
                        for addon_subject in signup["additional_subject_teacher"]:
                            additional_subject_teacher = AdditionalSubjectTeacherRelation.objects.filter(
                                id=from_global_id(addon_subject)[1],teacher__institution=institution_obj
                                ).exists()
                            
                            if additional_subject_teacher is not True:
                                raise GraphQLError('additional subject teacher ID is incorrect or does not belong to same institution')

                        additional_subject_teacher_ids.extend(signup["additional_subject_teacher"])

                    if subject_teacher_ids is not None:
                        student_section._subject_teacher = subject_teacher_ids

                    if additional_subject_teacher_ids is not None:
                        student_section._additional_subject_teacher = additional_subject_teacher_ids

                    student_section.save()


        return InitialStudentSignupMutation(institution=institution_obj)

                    

                    






class Mutation(graphene.ObjectType):
    initial_class_creation = InitialClassMutation.Field()
    initial_department_section_creation = InitialDepartmentSectionMutation.Field()
    initial_Teacher_signup = InitialTeacherSignupMutation.Field()
    initial_Student_signup = InitialStudentSignupMutation.Field()
    invite_user = InviteSend.Field()





'''
invite_user_json
x = {
    "teacher":[
        {
            "email":"",
            "register_number":""
        }
    ],
    "student":[
        {
            "email":"",
            "register_number":""
        }
    ]
}


class_json
x = {
    "class":[
        {
            "couse_id": "",
            "class_alias": "", -optional
            "class_division_id": "",
            "class_division_name": "",
            "additional_subject":[ -optional
                {
                    "subject_id": "",
                    "subject_type": ""
                }
            ]
        }
    ]
}




class_section_json
x = {
    "department_class":[
        {
            "department_name":"",
            "class":[
                {
                    "class_id":"",
                    "classDivision_section":[
                        {
                            "division_number":"",
                            "division_no_section":"",
                            "section":[] -optional
                        }
                    ]
                }
            ]
        }
    ]
}


teacher_json
x = {
    "teacher":[
        {
            "signup":
                {
                    "email":"",
                    "first_name":"",
                    "last_name":"",
                    "authority_role":"",
                    "register_number":""  
                },
            "positions": -optional
                {
                    "department":"", -optional
                    "class":"", -optional
                    "class_section":"" -optional
                },
            "class_subject":[ -optional
                {
                    "course_subject":"",
                    "section":[]
                }
            ],
            "class_additional_subject":[ -optional
                {
                    "addition_subject":"",
                    "section":[]
                }
            ]   
        }
    ]
}


student_json
x = {
    "student":[
        {
            "section":"",
            "session":"",
            "section_subject_teacher":[], -optional
            "additional_subject_teacher":[], -optional
            "signup":[
                {
                  "email":"",
                  "first_name":"",
                  "last_name":"",
                  "register_number":"",
                  "section_subject_teacher":[] -optional
                  "additional_subject_teacher":[] -optional
                }
            ]
        }
    ]
}

'''
import json
import datetime
from datetime import date, timedelta

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from account.permissions import UserAuthorizeTest

from .models import Announcement, CommentAnnouncementRelation, InstitutionAnnouncementRelation, DepartmentAnnouncementRelation,\
ClassAnnouncementRelation, SectionAnnouncementRelation, SubjectTeacherAnnouncementRelation,\
AdditionalSubjectTeacherAnnouncementRelation

from commentExplanation.models import Comment


class AnnouncementNode(DjangoObjectType):
    class Meta:
        model = Announcement
        filter_fields = []
        interfaces = (relay.Node, )


class CommentAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = CommentAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )


class InstitutionAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = InstitutionAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )

class DepartmentAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = DepartmentAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )

class ClassAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = ClassAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )

class SectionAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = SectionAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )

class SubjectTeacherAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = SubjectTeacherAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )

class AdditionalSubjectTeacherAnnouncementRelationNode(DjangoObjectType):
    class Meta:
        model = AdditionalSubjectTeacherAnnouncementRelation
        filter_fields = []
        interfaces = (relay.Node, )



class Query(graphene.ObjectType):

	institution_announcement = relay.Node.Field(InstitutionAnnouncementRelationNode)
	all_institution_announcement = DjangoFilterConnectionField(InstitutionAnnouncementRelationNode)

	department_announcement = relay.Node.Field(DepartmentAnnouncementRelationNode)
	all_department_announcement = DjangoFilterConnectionField(DepartmentAnnouncementRelationNode)

	class_announcement = relay.Node.Field(ClassAnnouncementRelationNode)
	all_class_announcement = DjangoFilterConnectionField(ClassAnnouncementRelationNode)

	section_announcement = relay.Node.Field(SectionAnnouncementRelationNode)
	all_section_announcement = DjangoFilterConnectionField(SectionAnnouncementRelationNode)

	subject_teacher_announcement = relay.Node.Field(SubjectTeacherAnnouncementRelationNode)
	all_subject_teacher_announcement = DjangoFilterConnectionField(SubjectTeacherAnnouncementRelationNode)

	additional_subject_teacher_announcement = relay.Node.Field(AdditionalSubjectTeacherAnnouncementRelationNode)
	all_additional_subject_teacher_announcement = DjangoFilterConnectionField(AdditionalSubjectTeacherAnnouncementRelationNode)



class AnnouncementUpdateDeleteMutation(relay.ClientIDMutation):
    institution_announcement = graphene.Field(InstitutionAnnouncementRelationNode)
    department_announcement = graphene.Field(DepartmentAnnouncementRelationNode)
    class_announcement = graphene.Field(ClassAnnouncementRelationNode)
    section_announcement = graphene.Field(SectionAnnouncementRelationNode)
    subject_teacher_announcement = graphene.Field(SubjectTeacherAnnouncementRelationNode)
    additional_subject_teacher_announcement = graphene.Field(AdditionalSubjectTeacherAnnouncementRelationNode)

    class Input:
        authority = graphene.String(required=True)
        announcement_relation_name = graphene.String(required=True)
        announcement_relation_id = graphene.String(required=True)
        announcement_status = graphene.String()
        announcement_block_comment = graphene.Boolean()
        announcement_archive_date = graphene.String()
        post_title = graphene.String()
        post_data = graphene.String()
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        authority_roles = (
            'adminUser','hod','classTeacher','sectionTeacher',
            'sectionSubjectTeacher','sectionAdditionalSubjectTeacher'
            )
        announcement_relation_names = (
            'institution_announcement','department_announcement','class_announcement',
            'section_announcement','subject_teacher_announcement','additional_subject_teacher_announcement'
            )

        if input.get('mutation_option') not in (2,3):
            raise GraphQLError('provide valide option')
        
        context = AnnouncementRelation(
            info,authority_roles,announcement_relation_names,
            input.get('authority'),
            input.get('announcement_relation_name'),
            input.get('announcement_relation_id')
            )

        result = context['result']
        annnouncement_relation_obj = context['annnouncement_relation_obj']

        if result[input.get('authority')] is not True:
            raise GraphQLError('you don\'t have proper permission. try different account')

        else:
            if input.get('mutation_option') == 2:
                if input.get('announcement_status') is not None or input.get('announcement_archive_date') is not None:
                    announcement_obj = annnouncement_relation_obj.announcement

                    if input.get('announcement_block_comment') is not None:
                        announcement_obj.block_comment = input.get('announcement_block_comment')

                    if input.get('announcement_status') is not None:
                        if announcement_obj.status == 'archive':
                            raise GraphQLError('you can change status of archive announcement')

                        if announcement_obj.status == 'active':
                            if input.get('announcement_status') == 'archive':
                                announcement_obj.status = 'archive'

                        if announcement_obj.status == 'draft':
                            if input.get('announcement_status') == 'active':
                               announcement_obj.status = 'active'
                               announcement_obj.publish = date.today()

                               if input.get('announcement_archive_date') is None:
                                  announcement_obj.archive_date = announcement_obj.publish + timedelta(days=10)

                               else:
                                   try:
                                      archive_date = datetime.datetime.strptime(input.get('announcement_archive_date'), '%Y-%m-%d').date()
                                   except ValueError:
                                      raise GraphQLError('Incorrect data format, should be YYYY-MM-DD')

                                   if archive_date < date.today():
                                      raise GraphQLError('archive date can\'t be in past')

                                   else:
                                       announcement_obj.archive_date = archive_date
                                       
                    announcement_obj.save()

                if input.get('post_title') is not None or input.get('post_data') is not None:
                    if annnouncement_relation_obj.announcement.status == 'archive':
                        raise GraphQLError('you can change archived announcement')

                    if input.get('announcement_status') == 'draft' or input.get('announcement_status') == 'active':
                        post_obj = annnouncement_relation_obj.announcement.post

                        if input.get('post_title') is not None:
                            post_obj.title = input.get('post_title')

                        if input.get('post_data') is not None:
                            json_string = input.get('post_data')
                            json_data = json.loads(json_string)
                            post_obj.data = json_data

                        post_obj.save()

                if input.get('announcement_relation_name') == 'institution_announcement':
                   return AnnouncementUpdateDeleteMutation(institution_announcement=annnouncement_relation_obj)

                if input.get('announcement_relation_name') == 'department_announcement':
                   return AnnouncementUpdateDeleteMutation(department_announcement=annnouncement_relation_obj)

                if input.get('announcement_relation_name') == 'class_announcement':
                   return AnnouncementUpdateDeleteMutation(class_announcement=annnouncement_relation_obj)

                if input.get('announcement_relation_name') == 'section_announcement':
                   return AnnouncementUpdateDeleteMutation(section_announcement=annnouncement_relation_obj)

                if input.get('announcement_relation_name') == 'subject_teacher_announcement':
                   return AnnouncementUpdateDeleteMutation(subject_teacher_announcement=annnouncement_relation_obj)

                if input.get('announcement_relation_name') == 'additional_subject_teacher_announcement':
                   return AnnouncementUpdateDeleteMutation(additional_subject_teacher_announcement=annnouncement_relation_obj)


            if input.get('mutation_option') == 3:
                annnouncement_relation_obj.announcement.post.delete()

                return AnnouncementUpdateDeleteMutation(institution_announcement=None)



class AnnouncementCommentMutation(relay.ClientIDMutation):
    announcement = graphene.Field(AnnouncementNode)
    comment_announcement = graphene.Field(CommentAnnouncementRelationNode)

    class Input:
        body = graphene.String()
        stared = graphene.Boolean()
        it_self = graphene.ID()
        comment_announcement_id = graphene.ID()
        announcement_relation_name = graphene.String(required=True)
        announcement_relation_id = graphene.String(required=True)
        authority = graphene.String(required=True)
        mutation_option = graphene.Int(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        def AnnouncementRelation(info,authority_roles,announcement_relation_names,authority,announcement_relation_name,announcement_relation_id):
            if announcement_relation_name not in announcement_relation_names:
                raise GraphQLError('provide proper values')

            if authority not in authority_roles:
                raise GraphQLError('provide proper values')

            if announcement_relation_name == 'institution_announcement':
                try:
                    annnouncement_relation_obj = InstitutionAnnouncementRelation.objects.select_related('institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except InstitutionAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('institution announcement ID is incorrect')

                institution_obj = annnouncement_relation_obj.institution
                result = UserAuthorizeTest(info, authority, institution_obj=institution_obj)


            if announcement_relation_name == 'department_announcement':
                try:
                    annnouncement_relation_obj = DepartmentAnnouncementRelation.objects.select_related('department__institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except DepartmentAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('department announcement ID is incorrect')

                department_obj = annnouncement_relation_obj.department
                result = UserAuthorizeTest(info, authority, department_obj=department_obj)


            if announcement_relation_name == 'class_announcement':
                try:
                    annnouncement_relation_obj = ClassAnnouncementRelation.objects.select_related('Class__institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except ClassAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('Class announcement ID is incorrect')

                class_obj = annnouncement_relation_obj.Class
                result = UserAuthorizeTest(info, authority, class_obj=class_obj)


            if announcement_relation_name == 'section_announcement':
                try:
                    annnouncement_relation_obj = SectionAnnouncementRelation.objects.select_related('section__which_division__Class__institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except SectionAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('section announcement ID is incorrect')

                class_section_obj = annnouncement_relation_obj.section
                result = UserAuthorizeTest(info, authority, class_section_obj=class_section_obj)


            if announcement_relation_name == 'subject_teacher_announcement':
                try:
                    annnouncement_relation_obj = SubjectTeacherAnnouncementRelation.objects.select_related('section_subject__section__which_division__Class__institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except SubjectTeacherAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('section subject announcement ID is incorrect')

                class_subject_teacher_obj = annnouncement_relation_obj.section_subject
                result = UserAuthorizeTest(info, authority, class_subject_teacher_obj=class_subject_teacher_obj)


            if announcement_relation_name == 'additional_subject_teacher_announcement':
                try:
                    annnouncement_relation_obj = AdditionalSubjectTeacherAnnouncementRelation.objects.select_related('section_additional_subject__section__which_division__Class__institution','announcement').get(
                        id=from_global_id(announcement_relation_id)[1]
                        )
                except AdditionalSubjectTeacherAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('additional subject announcement ID is incorrect')

                class_additional_subject_teacher_obj = annnouncement_relation_obj.section_additional_subject
                result = UserAuthorizeTest(info, authority, class_additional_subject_teacher_obj=class_additional_subject_teacher_obj)

            context = {'result':result, 'annnouncement_relation_obj':annnouncement_relation_obj}

            return context




        authority_roles = (
            'adminUser','institutionStudent',
            'hod', 'departmentStudent',
            'classTeacher', 'classStudent',
            'sectionTeacher', 'sectionStudent',
            'sectionSubjectTeacher', 'sectionStudentSubjectTeacher',
            'sectionAdditionalSubjectTeacher', 'sectionStudentAdditionalSubjectTeacher'
            )

        stared_authority = (
            'adminUser', 'hod','classTeacher',
            'sectionTeacher','sectionSubjectTeacher',
            'sectionAdditionalSubjectTeacher'
            )

        announcement_relation_names = (
            'institution_announcement', 'department_announcement',
            'class_announcement', 'section_announcement',
            'subject_teacher_announcement', 'additional_subject_teacher_announcement'
            )

        if input.get('mutation_option') not in (1,2):
            raise GraphQLError('provide valide mutation option')


        if input.get('mutation_option') is 1:
            context = AnnouncementRelation(
                info,authority_roles,announcement_relation_names,
                input.get('authority'),
                input.get('announcement_relation_name'),
                input.get('announcement_relation_id')
                )

        if input.get('mutation_option') is 2:
            context = AnnouncementRelation(
                info,stared_authority,announcement_relation_names,
                input.get('authority'),
                input.get('announcement_relation_name'),
                input.get('announcement_relation_id')
                )

        result = context['result']
        annnouncement_relation_obj = context['annnouncement_relation_obj']

        if result[input.get('authority')] is not True:
            raise GraphQLError('you don\'t have proper permission. try different account')

        if annnouncement_relation_obj.announcement.status != 'active':
            raise GraphQLError('you can\'t post comment on archived announcement')

        if annnouncement_relation_obj.announcement.block_comment:
            raise GraphQLError('comminting is blocked in this announcement')

        else:
            if input.get('mutation_option') == 1:
                if input.get('body') is None:
                    raise GraphQLError('provide comment text to post comment')

                else:
                    comment_obj = Comment(body=input.get('body'),commenter=info.context.user.nxtgenuser)

                    if input.get('it_self') is not None:
                        try:
                            self_comment_obj = Comment.objects.get(id=from_global_id(input.get('it_self'))[1])
                        except Comment.DoesNotExist:
                            raise GraphQLError('comment ID is incorrect')

                        if CommentAnnouncementRelation.objects.filter(announcement=annnouncement_relation_obj.announcement,comment=self_comment_obj).exists() is not True:
                            raise GraphQLError('comment does\'t not belong to the same announcement')

                        comment_obj.it_self = self_comment_obj

                    if input.get('stared') is not None:
                        if input.get('authority') in stared_authority:
                            comment_obj.stared = input.get('stared')

                    comment_obj._post_for = 'announcement'
                    comment_obj._post_model_obj = annnouncement_relation_obj.announcement
                    comment_obj.save()

                    return AnnouncementCommentMutation(announcement=annnouncement_relation_obj.announcement)


            if input.get('mutation_option') == 2:
                if input.get('stared') is None or input.get('comment_announcement_id') is None:
                    raise GraphQLError('provide proper value for updateing the comment')

                try:
                    comment_announcement_obj = CommentAnnouncementRelation.objects.select_related('comment','announcement').get(
                        id=from_global_id(input.get('comment_announcement_id'))[1]
                        )
                except CommentAnnouncementRelation.DoesNotExist:
                    raise GraphQLError('comment ID is incorrect')

                if comment_announcement_obj.announcement != annnouncement_relation_obj.announcement:
                    raise GraphQLError('you don\'t have the authority to update comment on this announcement')

                comment_obj = comment_announcement_obj.comment
                comment_obj.stared = input.get('stared')
                comment_obj.save()

                return AnnouncementCommentMutation(comment_announcement=comment_announcement_obj)









class Mutation(graphene.ObjectType):
    announcement_update_delete = AnnouncementUpdateDeleteMutation.Field()
    comment_announcement_create_update = AnnouncementCommentMutation.Field()


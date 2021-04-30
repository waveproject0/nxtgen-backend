import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from .models import TeacherProfile


class TeacherProfileNode(DjangoObjectType):
    class Meta:
        model = TeacherProfile
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    teacherProfile = relay.Node.Field(TeacherProfileNode)
    all_teacherProfile = DjangoFilterConnectionField(TeacherProfileNode)
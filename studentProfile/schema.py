import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from .models import StudentProfile




class StudentProfileNode(DjangoObjectType):
    class Meta:
        model = StudentProfile
        filter_fields = []
        interfaces = (relay.Node, )



class Query(graphene.ObjectType):
    student_profile = relay.Node.Field(StudentProfileNode)
    all_student_profile = DjangoFilterConnectionField(StudentProfileNode)
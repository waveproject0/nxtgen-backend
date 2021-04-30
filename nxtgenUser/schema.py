import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from .models import NxtgenUser


class NxtgenUserNode(DjangoObjectType):
    class Meta:
        model = NxtgenUser
        filter_fields = {
        	'student_profile': ['exact'],
        	'teacher_profile': ['exact'],
        	'management_profile': ['exact']
        }
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    relay_nxtgenUser = relay.Node.Field(NxtgenUserNode)
    relay_all_nxtgenUser = DjangoFilterConnectionField(NxtgenUserNode)
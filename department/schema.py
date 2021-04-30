import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from department.models import Department



class DepartmentNode(DjangoObjectType):
    class Meta:
        model = Department
        filter_fields = []
        interfaces = (relay.Node, )



class Query(graphene.ObjectType):
    deaprtment = relay.Node.Field(DepartmentNode)
    all_department = DjangoFilterConnectionField(DepartmentNode)
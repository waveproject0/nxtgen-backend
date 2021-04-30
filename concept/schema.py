import graphene
from django.db import IntegrityError
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from course.models import Subject
from .models import Concept




class ConceptNode(DjangoObjectType):
    class Meta:
        model = Concept
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
	concept = relay.Node.Field(ConceptNode)
	all_concept = DjangoFilterConnectionField(ConceptNode)


class ConceptMutation(relay.ClientIDMutation):
	concept = graphene.Field(ConceptNode)

	class Input:
		name = graphene.String()
		description = graphene.String()
		subject_id = graphene.ID()

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		


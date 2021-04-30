import graphene
import graphql_jwt
from django.dispatch import receiver
from graphql_jwt.refresh_token.signals import refresh_token_rotated, refresh_token_revoked

import institution.schema, account.schema, nxtgenUser.schema, teacherProfile.schema, studentProfile.schema, \
Class.schema, course.schema, department.schema, announcement.schema, post.schema, commentExplanation.schema,\
date.schema, attendance.schema, form.schema, bookmarkShare.schema, validationMatrix.schema,\
questionBank.schema, exam.schema
	


class Query(
	nxtgenUser.schema.Query, account.schema.Query, institution.schema.Query,
	teacherProfile.schema.Query, studentProfile.schema.Query, Class.schema.Query, course.schema.Query,
	department.schema.Query, announcement.schema.Query, date.schema.Query, attendance.schema.Query,
	form.schema.Query, bookmarkShare.schema.Query, validationMatrix.schema.Query, questionBank.schema.Query,
	exam.schema.Query,
	
	graphene.ObjectType
	):
    pass

class Mutation(
	account.schema.Mutation, institution.schema.Mutation, course.schema.Mutation,
	Class.schema.Mutation, post.schema.Mutation, announcement.schema.Mutation,
	commentExplanation.schema.Mutation, date.schema.Mutation, attendance.schema.Mutation,
	form.schema.Mutation, bookmarkShare.schema.Mutation, validationMatrix.schema.Mutation,
	questionBank.schema.Mutation, exam.schema.Mutation,

	graphene.ObjectType
	):
	token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
	verify_token = graphql_jwt.relay.Verify.Field()
	refresh_token = graphql_jwt.relay.Refresh.Field()
	revoke_token = graphql_jwt.relay.Revoke.Field()

	@receiver(refresh_token_rotated)
	def rotate_refresh_token(sender, request, refresh_token, **kwargs):
		refresh_token.revoke(request)
		refresh_token.delete()

	@receiver(refresh_token_revoked)
	def revoke_refresh_token(sender, request, refresh_token, **kwargs):
		refresh_token.delete()


class Subscription(account.schema.UserSubscription, graphene.ObjectType):
	pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
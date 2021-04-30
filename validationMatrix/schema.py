import graphene
from django.db import IntegrityError
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError

from form.models import FormPost, TopicFormQuery, SubTopicFormQuery, Explanation
from date.models import PublicDateInstitutionRelation
from questionBank.models import Question
from .models import LikeFormPost, LikePublicDate, LikeQuestion, QuestionIsCorrect, VoteExplanation, AbstractRelevance,\
RelevantTopicFormQuery, RelevantSubTopicFormQuery, QuestionDifficulty


class LikeFormPostNode(DjangoObjectType):
    class Meta:
        model = LikeFormPost
        filter_fields = []
        interfaces = (relay.Node, )

class LikePublicDateNode(DjangoObjectType):
    class Meta:
        model = LikePublicDate
        filter_fields = []
        interfaces = (relay.Node, )

class LikeQuestionNode(DjangoObjectType):
    class Meta:
        model = LikeQuestion
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionIsCorrectNode(DjangoObjectType):
    class Meta:
        model = QuestionIsCorrect
        filter_fields = []
        interfaces = (relay.Node, )


class VoteExplanationNode(DjangoObjectType):
    class Meta:
        model = VoteExplanation
        filter_fields = []
        interfaces = (relay.Node, )


class RelevantTopicFormQueryNode(DjangoObjectType):
    class Meta:
        model = RelevantTopicFormQuery
        filter_fields = []
        interfaces = (relay.Node, )

class RelevantSubTopicFormQueryNode(DjangoObjectType):
    class Meta:
        model = RelevantSubTopicFormQuery
        filter_fields = []
        interfaces = (relay.Node, )


class QuestionDifficultyNode(DjangoObjectType):
    class Meta:
        model = QuestionDifficulty
        filter_fields = []
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
	like_form_post = relay.Node.Field(LikeFormPostNode)
	all_like_form_post = DjangoFilterConnectionField(LikeFormPostNode)

	like_public_date = relay.Node.Field(LikePublicDateNode)
	all_like_public_date = DjangoFilterConnectionField(LikePublicDateNode)

	like_question = relay.Node.Field(LikeQuestionNode)
	all_like_question = DjangoFilterConnectionField(LikeQuestionNode)

	question_is_correct = relay.Node.Field(QuestionIsCorrectNode)
	all_question_is_correct = DjangoFilterConnectionField(QuestionIsCorrectNode)

	vote_explanation = relay.Node.Field(VoteExplanationNode)
	all_vote_explanation = DjangoFilterConnectionField(VoteExplanationNode)

	relevant_topic_form_query = relay.Node.Field(RelevantTopicFormQueryNode)
	all_relevant_topic_form_query = DjangoFilterConnectionField(RelevantTopicFormQueryNode)

	relevant_subTopic_form_query = relay.Node.Field(RelevantSubTopicFormQueryNode)
	all_relevant_subTopic_form_query = DjangoFilterConnectionField(RelevantSubTopicFormQueryNode)

	question_difficulty = relay.Node.Field(QuestionDifficultyNode)
	all_question_difficulty = DjangoFilterConnectionField(QuestionDifficultyNode)



class LikeMutation(relay.ClientIDMutation):
	form_post = graphene.Field(LikeFormPostNode)
	public_date = graphene.Field(LikePublicDateNode)
	question = graphene.Field(LikeQuestionNode)
	question_is_correct = graphene.Field(QuestionIsCorrectNode)

	class Input:
		like_to_id = graphene.ID()
		value = graphene.Boolean()
		like_relation_name = graphene.String(required=True)
		like_relation_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def like_return_mapping(like_relation_name, like_relation_obj=None):
			if like_relation_name == 'form_post':
				return LikeMutation(form_post=like_relation_obj)

			if like_relation_name == 'public_date':
				return LikeMutation(public_date=like_relation_obj)

			if like_relation_name == 'question':
				return LikeMutation(question=like_relation_obj)

			if like_relation_name == 'question_is_correct':
				return LikeMutation(question_is_correct=like_relation_obj)

		like_relation_names = ('form_post','public_date','question','question_is_correct')

		if input.get('like_relation_name') not in like_relation_names:
			raise GraphQLError('provide proper value.')

		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		user = info.context.user
		nextgen_user = user.nxtgenuser

		if user.is_authenticated and user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('like_to_id') is None or input.get('value') is None:
					raise GraphQLError('provide proper value')

				if input.get('like_relation_name') == 'form_post':
					try:
						form_post_obj = FormPost.objects.get(id=from_global_id(input.get('like_to_id'))[1])
					except FormPost.DoesNotExist:
						raise GraphQLError('form post ID is incorrect')

					like_relation_obj = LikeFormPost(user=nextgen_user,value=input.get('value'),form_post=form_post_obj)


				if input.get('like_relation_name') == 'public_date':
					try:
						public_date_obj = PublicDateInstitutionRelation.objects.get(id=from_global_id(input.get('like_to_id'))[1])
					except PublicDateInstitutionRelation.DoesNotExist:
						raise GraphQLError('public date ID is incorrect')

					like_relation_obj = LikePublicDate(user=nextgen_user,value=input.get('value'),public_date=public_date_obj)


				if input.get('like_relation_name') == 'question':
					try:
						question_obj = Question.objects.get(id=from_global_id(input.get('like_to_id'))[1])
					except Question.DoesNotExist:
						raise GraphQLError('question ID is incorrect')

					like_relation_obj = LikeQuestion(user=nextgen_user,value=input.get('value'),question=question_obj)


				if input.get('like_relation_name') == 'question_is_correct':
					try:
						question_obj = Question.objects.get(id=from_global_id(input.get('like_to_id'))[1])
					except Question.DoesNotExist:
						raise GraphQLError('question ID is incorrect')

					like_relation_obj = QuestionIsCorrect(user=nextgen_user,value=input.get('value'),question=question_obj)

				
				try:
					like_relation_obj.save()
				except IntegrityError:
					raise GraphQLError('you already liked or disliked')

				like_return_mapping(input.get('like_relation_name'),like_relation_obj)


			if input.get('mutation_option') in (2,3):
				if input.get('like_relation_id') is None:
					raise GraphQLError('provide proper value')

				if input.get('like_relation_name') == 'form_post':
					try:
						like_relation_obj = LikeFormPost.objects.select_related('user').get(
							id=from_global_id(input.get('like_relation_id'))[1]
							)
					except LikeFormPost.DoesNotExist:
						raise GraphQLError('form post like ID is incorrect')

				if input.get('like_relation_name') == 'public_date':
					try:
						like_relation_obj = LikePublicDate.objects.select_related('user').get(
							id=from_global_id(input.get('like_relation_id'))[1]
							)
					except LikePublicDate.DoesNotExist:
						raise GraphQLError('public date like ID is incorrect')

				if input.get('like_relation_name') == 'question':
					try:
						like_relation_obj = LikeQuestion.objects.select_related('user').get(
							id=from_global_id(input.get('like_relation_id'))[1]
							)
					except LikeQuestion.DoesNotExist:
						raise GraphQLError('question like ID is incorrect')


				if input.get('like_relation_name') == 'question_is_correct':
					try:
						like_relation_obj = QuestionIsCorrect.objects.select_related('user').get(
							id=from_global_id(input.get('like_relation_id'))[1]
							)
					except QuestionIsCorrect.DoesNotExist:
						raise GraphQLError('question_is_correct ID is incorrect')



				if like_relation_obj.user != nextgen_user:
					raise GraphQLError('you are not a valide user. try different account.')

				if input.get('mutation_option') == 2:
					if input.get('value') is None:
						raise GraphQLError('provide proper value')

					like_relation_obj.value = input.get('value')
					like_relation_obj.save()
					like_return_mapping(input.get('like_relation_name'),like_relation_obj)


				if input.get('mutation_option') == 3:
					like_relation_obj.delete()
					like_return_mapping(input.get('like_relation_name'))




class VoteMutation(relay.ClientIDMutation):
	explanation = graphene.Field(VoteExplanationNode)

	class Input:
		vote_to_id = graphene.ID()
		value = graphene.Boolean()
		vote_relation_name = graphene.String(required=True)
		vote_relation_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def vote_return_mapping(vote_relation_name, vote_relation_obj=None):
			if vote_relation_name == 'explanation':
				return VoteMutation(explanation=vote_relation_obj)

		vote_relation_names = ('explanation')

		if input.get('vote_relation_name') not in vote_relation_names:
			raise GraphQLError('provide proper value.')

		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		user = info.context.user
		nextgen_user = user.nxtgenuser

		if user.is_authenticated and user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('vote_to_id') is None or input.get('value') is None:
					raise GraphQLError('provide proper value')

				if input.get('vote_relation_name') == 'explanation':
					try:
						explanation_obj = Explanation.objects.get(id=from_global_id(input.get('vote_to_id'))[1])
					except Explanation.DoesNotExist:
						raise GraphQLError('explanation ID is incorrect')

					vote_relation_obj = VoteExplanation(user=nextgen_user,value=input.get('value'),explanation=explanation_obj)

				try:
					vote_relation_obj.save()
				except IntegrityError:
					raise GraphQLError('you already voted or dvoted')

				vote_return_mapping(input.get('vote_relation_name'),vote_relation_obj)


			if input.get('mutation_option') in (2,3):
				if input.get('vote_relation_id') is None:
					raise GraphQLError('provide proper value')

				if input.get('vote_relation_name') == 'explanation':
					try:
						vote_relation_obj = VoteExplanation.objects.select_related('user').get(
							id=from_global_id(input.get('vote_relation_id'))[1]
							)
					except VoteExplanation.DoesNotExist:
						raise GraphQLError('explanation vote ID is incorrect')

				if vote_relation_obj.user != nextgen_user:
					raise GraphQLError('you are not a valide user. try different account.')

				if input.get('mutation_option') == 2:
					if input.get('value') is None:
						raise GraphQLError('provide proper value')

					vote_relation_obj.value = input.get('value')
					vote_relation_obj.save()
					vote_return_mapping(input.get('vote_relation_name'),vote_relation_obj)


				if input.get('mutation_option') == 3:
					vote_relation_obj.delete()
					vote_return_mapping(input.get('vote_relation_name'))




class RelevantMutation(relay.ClientIDMutation):
	topic_form_query = graphene.Field(RelevantTopicFormQueryNode)
	subTopic_form_query = graphene.Field(RelevantSubTopicFormQueryNode)

	class Input:
		relevant_to_id = graphene.ID()
		value = graphene.String()
		relevant_relation_name = graphene.String(required=True)
		relevant_relation_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		def relevant_return_mapping(relevant_relation_name, relevant_relation_obj=None):
			if relevant_relation_name == 'topic_form_query':
				return RelevantMutation(topic_form_query=relevant_relation_obj)

		relevant_relation_names = ('topic_form_query','subTopic_form_query')

		if input.get('relevant_relation_name') not in relevant_relation_names:
			raise GraphQLError('provide proper value.')

		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		user = info.context.user
		nextgen_user = user.nxtgenuser

		if user.is_authenticated and user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('relevant_to_id') is None or input.get('value') is None:
					raise GraphQLError('provide proper value')

				if input.get('relevant_relation_name') == 'topic_form_query':
					try:
						topic_form_query_obj = TopicFormQuery.objects.get(id=from_global_id(input.get('relevant_to_id'))[1])
					except TopicFormQuery.DoesNotExist:
						raise GraphQLError('form query ID is incorrect')

					relevant_relation_obj = RelevantTopicFormQuery(user=nextgen_user,form_query=topic_form_query_obj)

				if input.get('relevant_relation_name') == 'subTopic_form_query':
					try:
						subTopic_form_query_obj = SubTopicFormQuery.objects.get(id=from_global_id(input.get('relevant_to_id'))[1])
					except SubTopicFormQuery.DoesNotExist:
						raise GraphQLError('form query ID is incorrect')

					relevant_relation_obj = RelevantTopicFormQuery(user=nextgen_user,form_query=subTopic_form_query_obj)

				
				valide_choice = False
				for choice in AbstractRelevance.RELEVANT_OPTION:
					if input.get('value') == choice[0]:
						valide_choice = True
						relevant_relation_obj.relevance = input.get('value')
						break

				if valide_choice is False:
					raise GraphQLError('provide proper value')
				
				try:
					relevant_relation_obj.save()
				except IntegrityError:
					raise GraphQLError('you already provided relevant value')

				relevant_return_mapping(input.get('relevant_relation_name'),relevant_relation_obj)


			if input.get('mutation_option') in (2,3):
				if input.get('relevant_relation_id') is None:
					raise GraphQLError('provide proper value')

				if input.get('relevant_relation_name') == 'topic_form_query':
					try:
						relevant_relation_obj = RelevantTopicFormQuery.objects.select_related('user').get(
							id=from_global_id(input.get('relevant_relation_id'))[1]
							)
					except RelevantTopicFormQuery.DoesNotExist:
						raise GraphQLError('form query vote ID is incorrect')

				if input.get('relevant_relation_name') == 'subTopic_form_query':
					try:
						relevant_relation_obj = RelevantSubTopicFormQuery.objects.select_related('user').get(
							id=from_global_id(input.get('relevant_relation_id'))[1]
							)
					except RelevantSubTopicFormQuery.DoesNotExist:
						raise GraphQLError('form query vote ID is incorrect')

				if relevant_relation_obj.user != nextgen_user:
					raise GraphQLError('you are not a valide user. try different account.')

				if input.get('mutation_option') == 2:
					if input.get('value') is None:
						raise GraphQLError('provide proper value')

					valide_choice = False
					for choice in AbstractRelevance.RELEVANT_OPTION:
						if input.get('value') == choice[0]:
							valide_choice = True
							relevant_relation_obj.relevance = input.get('value')
							break

					if valide_choice is False:
						raise GraphQLError('provide proper value')

					relevant_relation_obj.save()
					relevant_return_mapping(input.get('relevant_relation_name'),relevant_relation_obj)


				if input.get('mutation_option') == 3:
					relevant_relation_obj.delete()
					relevant_return_mapping(input.get('relevant_relation_name'))





class QuestionDifficultyMutation(relay.ClientIDMutation):
	question_difficulty = graphene.Field(QuestionDifficultyNode)

	class Input:
		question_id = graphene.ID()
		difficulty_option = graphene.String()
		question_difficulty_id = graphene.ID()
		mutation_option = graphene.Int(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutation_option') not in (1,2,3):
			raise GraphQLError('provide proper value')

		user = info.context.user
		nextgen_user = user.nxtgenuser

		if user.is_authenticated and user.is_active:
			if input.get('mutation_option') == 1:
				if input.get('question_id') is None or input.get('difficulty_option') is None:
					raise GraphQLError('provide complete information')

				try:
					question_obj = Question.objects.get(id=from_global_id(input.get('question_id'))[1])
				except Question.DoesNotExist:
					raise GraphQLError('question ID is incorrect')

				valide_choice = False
				for choice in QuestionDifficulty.DIFFICULTY_OPTION:
					if input.get('difficulty_option') == choice[0]:
						valide_choice = True
						break

				if valide_choice is False:
					raise GraphQLError('provide proper value')

				question_difficulty_obj = QuestionDifficulty.objects.get_or_create(
					user=nextgen_user,question=question_obj,difficulty_option=input.get('difficulty_option')
					)

				return QuestionDifficultyMutation(question_difficulty=question_difficulty_obj[0])


			if input.get('mutation_option') == 2:
				if input.get('difficulty_option') is None or input.get('question_difficulty_id') is None:
					raise GraphQLError('provide complete information')

				try:
					question_difficulty_obj = QuestionDifficulty.objects.select_related('user').get(
						id=from_global_id(input.get('question_difficulty_id'))[1]
						)
				except QuestionDifficulty.DoesNotExist:
					raise GraphQLError('question difficulty ID is incorrect')


				valide_choice = False
				for choice in QuestionDifficulty.DIFFICULTY_OPTION:
					if input.get('difficulty_option') == choice[0]:
						valide_choice = True
						break

				if valide_choice is False:
					raise GraphQLError('provide proper value')

				if nextgen_user != question_difficulty_obj.user:
					raise GraphQLError('you are no the valide user')

				question_difficulty_obj.difficulty_option = input.get('difficulty_option')

				question_difficulty_obj.save()

				return QuestionDifficultyMutation(question_difficulty=question_difficulty_obj)


			if input.get('mutation_option') == 3:
				if input.get('question_difficulty_id') is None:
					raise GraphQLError('provide complete information')

				try:
					question_difficulty_obj = QuestionDifficulty.objects.select_related('user').get(
						id=from_global_id(input.get('question_difficulty_id'))[1]
						)
				except QuestionDifficulty.DoesNotExist:
					raise GraphQLError('question difficulty ID is incorrect')

				if nextgen_user != question_difficulty_obj.user:
					raise GraphQLError('you are no the valide user')

				question_difficulty_obj.delete()

				return QuestionDifficultyMutation(question_difficulty=None)





class Mutation(graphene.ObjectType):
	like_mutation = LikeMutation.Field()
	vote_mutation = VoteMutation.Field()
	relevant_mutation = RelevantMutation.Field()
	question_difficulty_mutation = QuestionDifficultyMutation.Field()
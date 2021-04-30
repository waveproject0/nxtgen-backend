import graphene
from graphene.utils.str_converters import to_snake_case
from django.core.files.storage import FileSystemStorage
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_subscriptions.events import CREATED
from graphene_django.fields import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from graphene_file_upload.scalars import Upload
from .models import User, EmailToken
from institution.models import Institution, InstitutionTeacherRelation, AuthorityRole, SuperAdminControl

class AuthDjangoFilterConnectionField(DjangoFilterConnectionField):

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        if info.context.user.is_authenticated:

            qs = super(DjangoFilterConnectionField, cls).resolve_queryset(
                connection, iterable, info, args
            )
            filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
            qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

            order = args.get('orderBy', None)
            if order:
                if type(order) is str:
                    snake_order = to_snake_case(order)
                else:
                    snake_order = [to_snake_case(o) for o in order]
                qs = qs.order_by(*snake_order)
            return qs



class EmailTokenNode(DjangoObjectType):
    class Meta:
        model = EmailToken
        interfaces = (relay.Node, )

class UserNode(DjangoObjectType):
	class Meta:
		model = User
		exclude = ['is_active']
		filter_fields = {
			'first_name': ['exact', 'icontains', 'istartswith'],
		}
		interfaces = (relay.Node, )

	@classmethod
	def get_queryset(cls, queryset, info):
		if info.context.user.is_authenticated:
			print(info.context.user)
			return queryset.filter(id=info.context.user.id)

		else:
			print(queryset)
			return queryset.all()
'''
	@classmethod
	def get_node(cls, info, id):
		try:
			user = cls._meta.model.objects.get(id=id)
		except cls._meta.model.DoesNotExist:
			return None

		if info.context.user.is_authenticated:
			return user
		return None
'''


class Query(graphene.ObjectType):
	user = relay.Node.Field(UserNode)
	#all_user = DjangoConnectionField(UserNode)
	all_user = DjangoFilterConnectionField(UserNode)
	#all_user = AuthDjangoFilterConnectionField(UserNode, orderBy=graphene.List(of_type=graphene.String))


class BaseUserMutation(relay.ClientIDMutation):
	user = graphene.Field(UserNode)

	class Input:
		pk = graphene.ID()
		email = graphene.String()
		password = graphene.String()
		first_name = graphene.String()
		last_name = graphene.String()
		profile_picture = Upload()
		mutate_option = graphene.Int(required=True) # 1-create, 2-update, 3-delete

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		if input.get('mutate_option') not in (1,2,3): # checks for valide mutation option
			raise GraphQLError('Enter valide mutation option')
		else:
			if input.get('mutate_option') == 1: # create
				if input.get('email') and input.get('password') is not None:
					user = User.objects.create_user(
					email=input.get('email'), password=input.get('password'),
					first_name=input.get('first_name'),last_name=input.get('last_name'),
					is_active=False
					)
					if input.get('profile_picture'):
						print(input.get('profile_picture'))
						user.profile_picture.save(input.get('profile_picture').name, input.get('profile_picture'))
				else:
					raise GraphQLError('Provide Email and Password for creating user.')
			else:
				try:                                                                # tries to get the user from user.id 
					user = User.objects.get(id=from_global_id(input.get('pk'))[1])
				except(TypeError, ValueError, OverflowError, User.DoesNotExist):
					user = None                                                     # sets the user none if user does not exit
				if user is not None:
					if input.get('mutate_option') == 2: # update
						if input.get('first_name') is not None:
							user.first_name = input.get('first_name')
						if input.get('last_name') is not None:
							user.last_name = input.get('last_name')
						user.save()
					else:                      # delete
						user.delete()
						return BaseUserMutation(user=None)
				else:
					raise GraphQLError('user ID does not exit, provide a valide user ID.')
		return BaseUserMutation(user=user)


class SuperAdminCreateMutation(relay.ClientIDMutation):
	user = graphene.Field(UserNode)

	class Input:
		email = graphene.String(required=True)
		password = graphene.String(required=True)
		first_name = graphene.String(required=True)
		last_name = graphene.String(required=True)
		authority_role = graphene.ID(required=True)
		institute_name = graphene.String(required=True)
		address = graphene.String(required=True)
		geolocation_1 = graphene.Float(required=True)
		geolication_2 = graphene.Float(required=True)

	@classmethod
	def mutate_and_get_payload(cls, root, info, **input):
		user = User(														# creating base user
			email=input.get('email'), first_name=input.get('first_name'),
			last_name=input.get('last_name'), is_active=False
			)
		user.set_password(input.get('password'))                            # setting the password for the base user
		user._student_profile = False										# providing extra attr for additional arguments-
		user._teacher_profile = True										# on base user instance.
		user.save()

		institution = Institution.objects.create(							# creating institution 
			name=input.get('institute_name'), address=input.get('address'),
			geolocation=[input.get('geolocation_1'),input.get('geolocation_2')]
			)

		authority_role = AuthorityRole.objects.get(pk=from_global_id(input.get('authority_role'))[1]) # storing authority_role instance in veriable

		institution_teacher_relation = InstitutionTeacherRelation.objects.create(   # creating institution_teacher_relation
				institution=institution, teacher=user.nxtgenuser.teacherprofile,
				authority_role=authority_role
			)
		SuperAdminControl.objects.create(											# creating super_admin_control for institution
				institution_teacher=institution_teacher_relation
			)

		return SuperAdminCreateMutation(user=user)

class ImageUploadMutation(graphene.Mutation):
	image_url = graphene.String()

	class Arguments:
		image = Upload()
		multipleImage = graphene.Boolean(required=True)

	def mutate(self, info, image, multipleImage):
		if image:
			if multipleImage:
				for img in image:
					fs = FileSystemStorage()
					filename = fs.save(img.name, img)
					#uploaded_file_url = "http://127.0.0.1:8000" + fs.url(filename)
				return ImageUploadMutation(image_url="sucessfully uploaded")

			else:
				fs = FileSystemStorage()
				filename = fs.save(image.name, image)
				uploaded_file_url = "http://127.0.0.1:8000" + fs.url(filename)
				return ImageUploadMutation(image_url=uploaded_file_url)

		else:
			return ImageUploadMutation(image_url=None)



class UserSubscription(graphene.ObjectType):
	user_created = graphene.Field(UserNode)

	def resolve_user_created(root, info):
		return root.filter(
			lambda event:
				event.operation == CREATED and
				isinstance(event.instance, User)
		).map(lambda event: event.instance)





class Mutation(graphene.ObjectType):
	baseUser_signup = BaseUserMutation.Field()
	superAdminUser_signup = SuperAdminCreateMutation.Field()
	image_upload = ImageUploadMutation.Field()
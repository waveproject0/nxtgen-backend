"""Declare models for Custom User Model app."""

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .token import account_activation_token
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    profile_picture = models.ImageField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()



class EmailToken(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    token_url = models.URLField(max_length=500, unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email +" / "+ str(self.created_date)


#post_save signal
def create_emailtoken(sender, **kwargs):
    if kwargs['created']:
        user = kwargs['instance'] # creating token for email validation
        current_site = Site.objects.get_current().domain
        uid = urlsafe_base64_encode(force_bytes(user.id))
        email_token_instance = EmailToken.objects.create(user=user)
        token = account_activation_token.make_token(user)
        activation_link = "{0}/activate/{1}/{2}".format(current_site, uid, token)
        email_token_instance.token_url = activation_link
        email_token_instance.save() # saving the token into the database 
        '''
        subject = 'Activate Your Pinekown Account'
        message = "Hello {0}, {1}".format(user.first_name, activation_link)
        user.email_user(subject, message)
        '''


post_save.connect(create_emailtoken, sender=User)
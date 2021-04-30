from django.db.models.signals import post_save, post_delete
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

from .models import User

post_save.connect(post_save_subscription, sender=User, dispatch_uid="User_post_save")
post_delete.connect(post_delete_subscription, sender=User, dispatch_uid="User_post_delete")
from django.contrib import admin
from . import models

admin.site.register(models.Feedback)
admin.site.register(models.FeedbackMessage)
admin.site.register(models.FeedbackSupport)
from django.contrib import admin
from . import models

admin.site.register(models.PublicDateBookmark)
admin.site.register(models.FormPostBookmark)
admin.site.register(models.QuestionBookmark)

admin.site.register(models.FormPostShare)
admin.site.register(models.QuestionShare)
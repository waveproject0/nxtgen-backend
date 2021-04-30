from django.contrib import admin
from . import models

admin.site.register(models.Course)
admin.site.register(models.CourseSubjectRelation)
admin.site.register(models.Subject)
admin.site.register(models.SubjectTopicRelation)
admin.site.register(models.Topic)
admin.site.register(models.TopicSubTopicRelation)
admin.site.register(models.SubTopic)
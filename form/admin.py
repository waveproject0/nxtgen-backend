from django.contrib import admin
from . import models


admin.site.register(models.Form)
admin.site.register(models.FormPost)
admin.site.register(models.TopicFormQuery)
admin.site.register(models.SubTopicFormQuery)

admin.site.register(models.TopicQueryImproveRequest)
admin.site.register(models.SubTopicQueryImproveRequest)
admin.site.register(models.TopicExplanationImproveRequest)
admin.site.register(models.SubTopicExplanationImproveRequest)

admin.site.register(models.CommentFormPostRelation)
admin.site.register(models.CommentTopicFormQueryRelation)
admin.site.register(models.CommentSubTopicFormQueryRelation)
admin.site.register(models.ExplanationTopicFormQueryRelation)
admin.site.register(models.ExplanationSubTopicFormQueryRelation)
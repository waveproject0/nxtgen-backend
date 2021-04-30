from django.contrib import admin
from . import models

admin.site.register(models.LikeFormPost)
admin.site.register(models.LikePublicDate)
admin.site.register(models.LikeQuestion)

admin.site.register(models.QuestionIsCorrect)
admin.site.register(models.QuestionDifficulty)

admin.site.register(models.VoteExplanation)

admin.site.register(models.RelevantTopicFormQuery)
admin.site.register(models.RelevantSubTopicFormQuery)
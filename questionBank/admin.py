from django.contrib import admin
from . import models


admin.site.register(models.Question)

admin.site.register(models.QuestionExplanation)
admin.site.register(models.QuestionConcept)
admin.site.register(models.QuestionExam)

admin.site.register(models.QuestionSubjectRelation)
admin.site.register(models.QuestionTopicRelation)
admin.site.register(models.QuestionSubtopicRelation)
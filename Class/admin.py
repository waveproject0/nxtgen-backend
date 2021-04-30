from django.contrib import admin
from . import models

admin.site.register(models.Class)


admin.site.register(models.AdditionalSubject)
admin.site.register(models.ClassDivision)
admin.site.register(models.ClassWhichDivision)
admin.site.register(models.SessionStartDate)
admin.site.register(models.ClassSectionRelation)
admin.site.register(models.ClassStudentRelation)
admin.site.register(models.ClassSubjectTeacherRelation)
admin.site.register(models.AdditionalSubjectTeacherRelation)
admin.site.register(models.ClassStudentSubjectTeacherRelation)
admin.site.register(models.ClassStudentAdditionalSubjectTeacherRelation)
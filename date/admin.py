from django.contrib import admin
from . import models


admin.site.register(models.Date)

admin.site.register(models.DateInstitutionRelation)
admin.site.register(models.PublicDateInstitutionRelation)

admin.site.register(models.DateDepartmentRelation)
admin.site.register(models.DateClassRelation)
admin.site.register(models.DateSectionRelation)
admin.site.register(models.DateSubjectTeacherRelation)
admin.site.register(models.DateAdditionalSubjectTeacherRelation)
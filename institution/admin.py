from django.contrib import admin
from . import models


admin.site.register(models.BoardAffiliation)
admin.site.register(models.InstituteType)
admin.site.register(models.AuthorityRole)
admin.site.register(models.Institution)
admin.site.register(models.InstitutionTeacherRelation)
admin.site.register(models.InstitutionStudentRelation)
admin.site.register(models.SuperAdminControl)
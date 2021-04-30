from django.contrib import admin
from . import models


admin.site.register(models.InstitutionGroup)
admin.site.register(models.GroupInstitutionRelation)
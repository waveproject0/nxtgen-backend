from django.contrib import admin
from . import models


admin.site.register(models.TeacherProfile)
admin.site.register(models.TeacherFollowerRelation)
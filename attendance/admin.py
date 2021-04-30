from django.contrib import admin
from . import models


admin.site.register(models.SubjectTeacherAttendance)
admin.site.register(models.AdditionalSubjectTeacherAttendance)

admin.site.register(models.SubjectAttendee)
admin.site.register(models.AdditionalSubjectAttendee)
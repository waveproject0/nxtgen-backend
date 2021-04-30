from django.contrib import admin
from . import models

admin.site.register(models.Announcement)
admin.site.register(models.CommentAnnouncementRelation)
admin.site.register(models.InstitutionAnnouncementRelation)
admin.site.register(models.DepartmentAnnouncementRelation)
admin.site.register(models.ClassAnnouncementRelation)
admin.site.register(models.SectionAnnouncementRelation)
admin.site.register(models.SubjectTeacherAnnouncementRelation)
admin.site.register(models.AdditionalSubjectTeacherAnnouncementRelation)

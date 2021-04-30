from django.contrib import admin
from . import models


admin.site.register(models.WebLink)
admin.site.register(models.Resource)
admin.site.register(models.ResourceCollection)
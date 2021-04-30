from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView
from graphql_jwt.decorators import jwt_cookie
from django.urls import path, re_path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    #path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),

    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),

    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

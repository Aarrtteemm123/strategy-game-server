from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django_mongoengine import mongo_admin
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mongoadmin/', mongo_admin.site.urls),
    url(r'^', include('polls.urls')),
    url(r'^auth/obtain_token/', obtain_jwt_token),
    url(r'^auth/refresh_token/', refresh_jwt_token),
]
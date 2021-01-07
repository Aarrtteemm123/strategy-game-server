from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django_mongoengine import mongo_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mongoadmin/', mongo_admin.site.urls),
    url(r'^', include('polls.urls')),
]
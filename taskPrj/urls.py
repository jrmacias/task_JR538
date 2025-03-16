"""
URL configuration for taskPrj project.
"""
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path("api/", include(('taskApi.urls', 'api'), namespace='api')),
    path("admin/", admin.site.urls, name="admin"),
    path('', include(('taskWebapp.urls', 'web'), namespace='web')),
]

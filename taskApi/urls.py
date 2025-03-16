"""
URL configuration for taskApi application.
"""
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from taskApi import views
from taskPrj import settings

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

router.register(r"repositories", views.DatasetRepositoryInfoView)

schema_view = get_schema_view(
    openapi.Info(
        title=settings.API_NAME+" API",
        default_version=settings.REST_FRAMEWORK["DEFAULT_VERSION"],
        description="API documentation for Task " + settings.API_NAME,
        contact=openapi.Contact(email=settings.API_CONTACT_EMAIL),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(router.urls), name="rest_ui"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path("dataset/<slug:accession>/",
         views.view_DatasetDetails, name='dataset_details'),

    # Swagger documentation
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # ReDoc documentation
    path("redoc/",
         schema_view.with_ui("redoc", cache_timeout=0),
         name="schema-redoc"),
]

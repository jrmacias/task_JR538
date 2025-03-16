"""
URL configuration for taskWebapp application.
"""

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # path("search/", views.seach_dataset, name="ds_search"),

    path('details/<accession>/', views.ds_details_view, name='ds_details'),

    path('search/', views.get_dataset, name='search'),

    path('download/<slug:accession>/metadata/',
         views.download_file,
         name='download_metadata_file'),

]

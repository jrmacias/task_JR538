""" 
This module contains the admin configuration for the taskApi app. 
"""
from django.contrib import admin
from . import models


class DatasetRepositoryFileInline(admin.TabularInline):
    model = models.DatasetRepositoryFile
    extra = 0


@admin.register(models.DatasetRepository)
class DatasetRepositoryAdmin(admin.ModelAdmin):
    model = models.DatasetRepository
    empty_value_display = "-empty-"

    list_display = ("id", "name", "accession_prefix", "repository_website")
    search_fields = ("name", "accession_template")
    ordering = ("name",)
    list_per_page = 10
    list_max_show_all = 100
    list_select_related = True
    list_display_links = ("id", "name")

    inlines = [DatasetRepositoryFileInline]


class DatasetFileInline(admin.TabularInline):
    model = models.DatasetFile
    extra = 0


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    model = models.Dataset
    empty_value_display = "-empty-"

    list_display = ("accession", "repository", "title", "description")
    search_fields = ("title", "description")
    list_filter = ("repository",)
    ordering = ("accession",)
    list_per_page = 10
    list_max_show_all = 100
    list_select_related = True
    list_display_links = ("accession",)

    inlines = [DatasetFileInline]

@admin.register(models.DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    model = models.DatasetFile
    empty_value_display = "-empty-"

    list_display = ("id", "dataset", "file", "description")
    list_filter = ("dataset",)
    ordering = ("dataset",)
    list_per_page = 10
    list_max_show_all = 100
    list_select_related = True
    list_display_links = ("id",)
from django.contrib import admin

from .models import LabProfile, Teacher


@admin.register(LabProfile)
class LabProfileAdmin(admin.ModelAdmin):
    """实验室概况：后台只维护一条记录。"""

    list_display = ["slogan", "founded_year", "contact"]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "title", "research"]
    ordering = ["order", "id"]
    search_fields = ["name", "title"]

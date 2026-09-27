from django.contrib import admin

from .models import LabProfile, Teacher


@admin.register(LabProfile)
class LabProfileAdmin(admin.ModelAdmin):
    """实验室概况：后台只维护一条记录。"""

    list_display = ["slogan", "founded_year", "contact"]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "title", "research"]   # 显示列
    ordering = ["order", "id"]                              # 默认按 order 排序
    search_fields = ["name", "title"]                       # 页面中出现搜索框，可以按name和title检索

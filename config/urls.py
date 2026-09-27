"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path

from core.views import home, recruit
from lab.views import profile, teachers

admin.site.site_header = "FVIL 飞行器创新实验室管理后台"
admin.site.site_title = "FVIL 飞行器创新实验室"
admin.site.index_title = "内容管理"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("about/", profile, name="lab_profile"),
    path("about/teachers/", teachers, name="lab_teachers"),
    path("recruit/", recruit, name="recruit"),
]

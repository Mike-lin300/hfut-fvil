"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path

from core.views import home

admin.site.site_header = "FVIL 飞行器创新实验室管理后台"
admin.site.site_title = "FVIL 飞行器创新实验室"
admin.site.index_title = "内容管理"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]

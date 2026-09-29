"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path

from core.views import guide, home, recruit
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
    re_path(r"^guide/(?P<path>.*)$", guide, name="guide"),
]

# 开发环境服务用户上传的媒体文件（生产环境由 Web 服务器处理）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

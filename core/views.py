from django.conf import settings
from django.shortcuts import render
from django.views.static import serve

from lab.models import LabProfile


def home(request):
    """主页：hero + 简介摘要 + 招新入口（视觉打磨在 T1-4/T1-5）。"""
    profile = LabProfile.objects.first()
    return render(request, "core/home.html", {"profile": profile})


def guide(request, path=""):
    """导学站静态展示（T2-1 临时方案）：实时读盘 fvil-ec-guide/web，空路径默认 index.html。"""
    return serve(request, path or "index.html", document_root=settings.GUIDE_ROOT)

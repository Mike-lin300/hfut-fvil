from django.shortcuts import render

from lab.models import LabProfile


def home(request):
    """主页：hero + 简介摘要 + 招新入口（视觉打磨在 T1-4/T1-5）。"""
    profile = LabProfile.objects.first()
    return render(request, "core/home.html", {"profile": profile})


def recruit(request):
    """招新占位页：阶段2 接入真实报名。"""
    return render(request, "core/recruit.html")

from django.shortcuts import render

from .models import LabProfile, Teacher


def profile(request):
    """实验室概况页。"""
    profile = LabProfile.objects.first()
    return render(request, "lab/profile.html", {"profile": profile})


def teachers(request):
    """指导老师列表。"""
    teachers = Teacher.objects.all()
    return render(request, "lab/teachers.html", {"teachers": teachers})

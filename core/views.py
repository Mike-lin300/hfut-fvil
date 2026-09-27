from django.shortcuts import render


def home(request):
    """主页占位视图：阶段1 填充真实内容。"""
    return render(request, "core/home.html")

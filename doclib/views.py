from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import SubmissionForm
from .models import Assignment, Document


def doclib_home(request):
    """材料库（导学材料双形态之"文档材料"）：按分类分组展示，公开下载。"""
    docs = list(Document.objects.select_related("uploader").order_by("category", "-id"))
    categories = [
        ("guide", "导学材料"),
        ("homework", "作业文件"),
        ("appendix", "附录"),
        ("other", "其他"),
    ]
    groups = []
    for key, label in categories:
        items = [d for d in docs if d.category == key]
        if items:
            groups.append({"key": key, "label": label, "items": items})
    return render(request, "doclib/home.html", {"groups": groups})


def assignment_list(request):
    """作业列表：发布 PDF 可下载 + 截止信息 + 提交入口（公开，无需登录）。"""
    assignments = Assignment.objects.select_related("batch").order_by("-id")
    return render(request, "doclib/assignments.html", {"assignments": assignments})


def assignment_submit(request, pk):
    """作业提交：学号+姓名校验报名库 → report.pdf + source.zip 双文件 → 命名/类型/唯一校验。"""
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, assignment=assignment)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('assignment_submit', args=[pk])}?ok=1")
    else:
        form = SubmissionForm(assignment=assignment)
    return render(
        request,
        "doclib/submit.html",
        {"assignment": assignment, "form": form, "ok": request.GET.get("ok") == "1"},
    )

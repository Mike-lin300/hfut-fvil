from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

import openpyxl

from .forms import QueryForm, SignupForm
from .models import Applicant, Batch, Score


def recruit_home(request):
    """招新入口：当前批次状态 + 报名/查询入口。"""
    current = Batch.objects.filter(status="open").order_by("-id").first()
    batches = Batch.objects.order_by("-id")[:5]
    return render(request, "recruitment/home.html", {"current": current, "batches": batches})


def signup(request):
    """报名：仅当前存在 status=open 批次时可提交；学号唯一（表单校验 + DB 兜底）；不收集意向方向。"""
    current = Batch.objects.filter(status="open").order_by("-id").first()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if not current:
            return render(
                request, "recruitment/signup.html",
                {"form": form, "current": None, "closed": True},
            )
        if form.is_valid():
            applicant = form.save(batch=current)
            return render(request, "recruitment/signup_success.html", {"applicant": applicant})
        return render(request, "recruitment/signup.html", {"form": form, "current": current})
    return render(request, "recruitment/signup.html", {"form": SignupForm(), "current": current})


def query(request):
    """匿名成绩查询：学号 + 姓名 → 各轮次等级与评价（无需账号登录）。"""
    form = QueryForm(request.GET or None)
    result = None
    if form.is_valid():
        result = (
            Applicant.objects.filter(
                student_id=form.cleaned_data["student_id"],
                name=form.cleaned_data["name"],
            )
            .select_related("batch")
            .prefetch_related("scores__round")
            .first()
        )
        if result is None:
            form.add_error(None, "未找到匹配的报名记录，请核对学号与姓名。")
    return render(request, "recruitment/query.html", {"form": form, "result": result})


@login_required
def export(request):
    """数据导出（Excel）：仅「招新管理员」组成员可用；报名名单 + 成绩两个工作表。"""
    user = request.user
    if not (user.is_staff and user.groups.filter(name="招新管理员").exists()):
        return HttpResponseForbidden("仅「招新管理员」可导出数据。")

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "报名名单"
    ws1.append(["编号", "批次", "姓名", "学号", "年级", "专业", "联系方式", "状态", "报名时间", "备注"])
    qs1 = Applicant.objects.select_related("batch").order_by("batch_id", "sid")
    for a in qs1:
        ws1.append([
            a.sid, a.batch.name, a.name, a.student_id, a.grade, a.major, a.contact,
            a.get_status_display(),
            a.signup_time.strftime("%Y-%m-%d %H:%M") if a.signup_time else "",
            a.remark,
        ])

    ws2 = wb.create_sheet("成绩")
    ws2.append(["编号", "批次", "姓名", "学号", "轮次", "等级", "评价", "录入人", "录入时间"])
    qs2 = Score.objects.select_related("applicant__batch", "round", "entered_by").order_by(
        "applicant__batch_id", "applicant__sid", "round_id"
    )
    for s in qs2:
        ws2.append([
            s.applicant.sid, s.applicant.batch.name, s.applicant.name, s.applicant.student_id,
            s.round.name, s.grade, s.comment,
            s.entered_by.username if s.entered_by else "",
            s.entered_at.strftime("%Y-%m-%d %H:%M") if s.entered_at else "",
        ])

    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = 'attachment; filename="fvil_recruit_export.xlsx"'
    wb.save(resp)
    return resp

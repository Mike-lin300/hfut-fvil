from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import path

from utils.excel import export_xlsx_response

from .models import Applicant, Batch, Round, Score


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "signup_start", "signup_end"]
    list_filter = ["status"]
    search_fields = ["name"]


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ["sid", "name", "student_id", "grade", "major", "batch", "status", "signup_time"]
    list_filter = ["batch", "status", "grade"]
    search_fields = ["sid", "name", "student_id", "major"]
    list_per_page = 50
    actions = ["bulk_score", "export_selected_xlsx"]
    change_list_template = "admin/export_all_change_list.html"

    APPLICANT_HEADERS = ["编号", "批次", "姓名", "学号", "年级", "专业", "QQ", "状态", "报名时间", "备注"]

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path(
                "export-all/", self.admin_site.admin_view(self.export_all_view),
                name="%s_%s_export-all" % info,
            ),
        ] + urls

    def export_all_view(self, request):
        """独立按钮：一键导出全部报名者。"""
        if not request.user.has_perm("recruitment.change_applicant"):
            raise PermissionDenied
        return export_xlsx_response(
            self.APPLICANT_HEADERS, self._applicant_rows(Applicant.objects.all()),
            "fvil_applicants_all.xlsx",
        )

    def _applicant_rows(self, qs):
        rows = []
        for a in qs.select_related("batch").order_by("batch_id", "sid"):
            rows.append([
                a.sid, a.batch.name, a.name, a.student_id, a.grade, a.major, a.contact,
                a.get_status_display(),
                a.signup_time.strftime("%Y-%m-%d %H:%M") if a.signup_time else "",
                a.remark,
            ])
        return rows

    @admin.action(description="导出 Excel（选中报名者）")
    def export_selected_xlsx(self, request, queryset):
        return export_xlsx_response(
            self.APPLICANT_HEADERS, self._applicant_rows(queryset),
            "fvil_applicants_selected.xlsx",
        )

    @admin.action(description="批量录入成绩（选定报名者 → 选择轮次/等级/评价）")
    def bulk_score(self, request, queryset):
        if "apply" in request.POST:
            round_id = request.POST.get("round_id")
            grade = request.POST.get("grade")
            comment = request.POST.get("comment", "")
            if not round_id or not grade:
                self.message_user(request, "请选择轮次和等级。", level=messages.ERROR)
                return redirect(request.get_full_path())
            r = Round.objects.filter(id=round_id).first()
            if r is None:
                self.message_user(request, "轮次不存在。", level=messages.ERROR)
                return redirect(request.get_full_path())
            created = skipped = 0
            for a in queryset:
                _, was_created = Score.objects.get_or_create(
                    applicant=a,
                    round=r,
                    defaults={"grade": grade, "comment": comment, "entered_by": request.user},
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
            self.message_user(request, f"已录入 {created} 条成绩；跳过已存在 {skipped} 条。")
            return redirect(request.get_full_path())
        return render(
            request,
            "admin/recruitment/applicant/bulk_score.html",
            {
                "applicants": queryset,
                "rounds": Round.objects.order_by("batch_id", "id"),
                "grades": Score.GRADE_CHOICES,
                "opts": Applicant._meta,
            },
        )


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ["batch", "name", "round_type", "date"]
    list_filter = ["batch", "round_type"]
    search_fields = ["name"]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["applicant", "round", "grade", "entered_by", "entered_at"]
    list_filter = ["round__batch", "round", "grade"]
    search_fields = ["applicant__name", "applicant__student_id"]
    actions = ["export_selected_xlsx"]
    change_list_template = "admin/export_all_change_list.html"

    SCORE_HEADERS = ["编号", "批次", "姓名", "学号", "轮次", "等级", "评价", "录入人", "录入时间"]

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path(
                "export-all/", self.admin_site.admin_view(self.export_all_view),
                name="%s_%s_export-all" % info,
            ),
        ] + urls

    def export_all_view(self, request):
        """独立按钮：一键导出全部成绩。"""
        if not request.user.has_perm("recruitment.change_score"):
            raise PermissionDenied
        return export_xlsx_response(
            self.SCORE_HEADERS, self._score_rows(Score.objects.all()),
            "fvil_scores_all.xlsx",
        )

    def _score_rows(self, qs):
        rows = []
        for s in qs.select_related("applicant__batch", "round", "entered_by").order_by(
            "applicant__batch_id", "applicant__sid", "round_id"
        ):
            rows.append([
                s.applicant.sid, s.applicant.batch.name, s.applicant.name,
                s.applicant.student_id, s.round.name, s.grade, s.comment,
                s.entered_by.username if s.entered_by else "",
                s.entered_at.strftime("%Y-%m-%d %H:%M") if s.entered_at else "",
            ])
        return rows

    @admin.action(description="导出 Excel（选中成绩）")
    def export_selected_xlsx(self, request, queryset):
        return export_xlsx_response(
            self.SCORE_HEADERS, self._score_rows(queryset),
            "fvil_scores_selected.xlsx",
        )

    def save_model(self, request, obj, form, change):
        """录入成绩时自动记录录入人（未显式指定时）。"""
        if not obj.entered_by_id:
            obj.entered_by = request.user
        super().save_model(request, obj, form, change)

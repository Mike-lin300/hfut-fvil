from django.contrib import admin, messages
from django.shortcuts import redirect, render

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
    actions = ["bulk_score"]

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

    def save_model(self, request, obj, form, change):
        """录入成绩时自动记录录入人（未显式指定时）。"""
        if not obj.entered_by_id:
            obj.entered_by = request.user
        super().save_model(request, obj, form, change)

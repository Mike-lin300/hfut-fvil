from django.contrib import admin

from .models import Applicant, Batch, Round, Score


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "signup_start", "signup_end"]
    list_filter = ["status"]
    search_fields = ["name"]


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ["name", "student_id", "grade", "major", "batch", "status", "signup_time"]
    list_filter = ["batch", "status", "grade"]
    search_fields = ["name", "student_id", "major"]
    list_per_page = 50


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

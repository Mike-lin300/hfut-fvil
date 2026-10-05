from django.contrib import admin

from .models import Assignment, Document, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["batch", "title", "deadline", "file", "round", "created_at"]
    list_filter = ["batch"]
    search_fields = ["title", "description"]
    readonly_fields = ["round", "created_at"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["assignment", "student_id", "name", "report", "source", "submitted_at"]
    list_filter = ["assignment__batch", "assignment"]
    search_fields = ["student_id", "name"]
    readonly_fields = [
        "assignment", "applicant", "student_id", "name", "report", "source",
        "submitted_at", "grading_note",
    ]
    list_per_page = 50

    @admin.display(description="批改说明")
    def grading_note(self, obj):
        return (
            "下载 report 批改后，在「招新报名者」列表中勾选该生 → 批量录入成绩"
            "（选择作业轮次 + 等级 + 评价）；学生可在「招新入口 → 成绩查询」查看。"
        )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "file", "uploaded_at", "uploader"]
    list_filter = ["category"]
    search_fields = ["title", "description"]

    def save_model(self, request, obj, form, change):
        """上传材料时自动记录上传人。"""
        if not obj.uploader_id:
            obj.uploader = request.user
        super().save_model(request, obj, form, change)

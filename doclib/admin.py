import io
import zipfile

from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Assignment, Document, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["batch", "title", "deadline", "file", "round", "created_at"]
    list_filter = ["batch"]
    search_fields = ["title", "description"]
    readonly_fields = ["round", "created_at"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "assignment", "student_id", "name",
        "report_link", "source_link", "grade_link", "submitted_at",
    ]
    list_filter = ["assignment__batch", "assignment"]
    search_fields = ["student_id", "name"]
    readonly_fields = [
        "assignment", "applicant", "student_id", "name", "report", "source",
        "submitted_at", "grading_note",
    ]
    list_per_page = 50
    actions = ["bulk_download_source"]

    @admin.display(description="报告 (PDF)")
    def report_link(self, obj):
        """报告 PDF：新标签页打开（浏览器原生预览），方便回到列表页继续处理。"""
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">查看 / 下载</a>', obj.report.url
        )

    @admin.display(description="源代码 (ZIP)")
    def source_link(self, obj):
        return format_html('<a href="{}" download>下载</a>', obj.source.url)

    @admin.display(description="录入成绩")
    def grade_link(self, obj):
        """一键跳转：新标签页打开成绩添加页，学号/作业轮次已预填，只需选等级+评价。"""
        if obj.applicant_id and obj.assignment.round_id:
            url = (
                f"/admin/recruitment/score/add/"
                f"?applicant={obj.applicant_id}&round={obj.assignment.round_id}"
            )
            return format_html(
                '<a class="button" href="{}" target="_blank" rel="noopener">录入成绩</a>', url
            )
        return "—"

    @admin.display(description="批改说明")
    def grading_note(self, obj):
        return (
            "工作流：报告列点击「查看/下载」（新标签页预览 PDF）→ 回到本页点「录入成绩」"
            "（新标签页，学号与作业轮次已预填）→ 选等级 + 评价保存；"
            "学生可在「招新入口 → 成绩查询」查看。"
        )

    @admin.action(description="批量下载源代码（打包 ZIP）")
    def bulk_download_source(self, request, queryset):
        """勾选一批提交 → 打包为一个 ZIP，内部按「作业标题/学号_姓名_source.zip」组织，防止混淆。"""
        buf = io.BytesIO()
        count = 0
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for sub in queryset.select_related("assignment").order_by(
                "assignment_id", "student_id"
            ):
                arcname = f"{sub.assignment.title}/{sub.student_id}_{sub.name}_source.zip"
                try:
                    zf.write(sub.source.path, arcname=arcname)
                    count += 1
                except (FileNotFoundError, ValueError, OSError):
                    continue
        if count == 0:
            self.message_user(request, "所选提交没有可下载的源代码文件。", level=messages.ERROR)
            return
        resp = HttpResponse(buf.getvalue(), content_type="application/zip")
        resp["Content-Disposition"] = 'attachment; filename="fvil_submissions_source.zip"'
        self.message_user(request, f"已打包 {count} 份源代码。")
        return resp


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

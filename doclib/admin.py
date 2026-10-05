import io
import zipfile

from django.contrib import admin, messages
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Assignment, Document, Submission
from recruitment.models import Score


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
        "report_link", "source_link", "grade_status", "submitted_at",
    ]
    list_filter = ["assignment__batch", "assignment"]
    search_fields = ["student_id", "name"]
    readonly_fields = [
        "assignment", "applicant", "student_id", "name", "report", "source",
        "submitted_at", "grading_note",
    ]
    list_per_page = 50
    actions = ["bulk_download_source"]

    def get_ordering(self, request):
        """未评分（is_graded=0）排前、已评分沉底；同组内最新提交在前。"""
        return ["is_graded", "-submitted_at"]

    def get_queryset(self, request):
        """标注是否已按本作业轮次评分（用于排序与列表直接展示等级）。
        不调用 super().get_queryset()：其会先按 get_ordering 排序，
        而 is_graded 需在 annotate 之后才能引用。"""
        qs = self.model._default_manager.get_queryset()
        graded = Score.objects.filter(
            applicant=OuterRef("applicant_id"),
            round=OuterRef("assignment__round_id"),
        )
        return qs.annotate(is_graded=Exists(graded)).prefetch_related(
            "applicant__scores", "assignment__round"
        )

    @admin.display(description="报告 (PDF)")
    def report_link(self, obj):
        """报告 PDF：新标签页打开（浏览器原生预览），方便回到列表页继续处理。"""
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">查看 / 下载</a>', obj.report.url
        )

    @admin.display(description="源代码 (ZIP)")
    def source_link(self, obj):
        return format_html('<a href="{}" download>下载</a>', obj.source.url)

    @admin.display(description="评分")
    def grade_status(self, obj):
        """已评分：直接显示等级 + 查看/修改入口；未评分：一键录入成绩（新标签页，预填学号与轮次）。"""
        score = None
        if obj.applicant_id and obj.assignment.round_id:
            score = next(
                (s for s in obj.applicant.scores.all() if s.round_id == obj.assignment.round_id),
                None,
            )
        if score is not None:
            return format_html(
                '<span class="badge text-bg-success">{}</span> '
                '<a href="/admin/recruitment/score/{}/change/" target="_blank" rel="noopener">查看</a>',
                score.grade, score.id,
            )
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
            "列表按「未评分 → 已评分」排序，未评分的在顶部、已评分的沉底，"
            "每行评分列直接显示等级。工作流：报告列「查看/下载」（新标签页预览 PDF）"
            "→ 回本页「录入成绩」（新标签页，学号与作业轮次已预填）→ 选等级 + 评价保存；"
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

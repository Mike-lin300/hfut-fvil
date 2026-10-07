import io
import os
import zipfile

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html

from utils.excel import export_xlsx_response

from .models import Assignment, Document, Submission
from recruitment.models import Score


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["batch", "title", "deadline", "file", "round", "created_at"]
    list_filter = ["batch"]
    search_fields = ["title", "description"]
    readonly_fields = ["round", "created_at"]
    actions = ["export_selected_xlsx"]
    change_list_template = "admin/export_all_change_list.html"

    ASSIGNMENT_HEADERS = ["批次", "标题", "截止时间", "文件", "创建时间"]

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
        """独立按钮：一键导出全部作业。"""
        if not request.user.has_perm("doclib.change_assignment"):
            raise PermissionDenied
        return export_xlsx_response(
            self.ASSIGNMENT_HEADERS, self._assignment_rows(Assignment.objects.all()),
            "fvil_assignments_all.xlsx",
        )

    def _assignment_rows(self, qs):
        rows = []
        for a in qs.select_related("batch").order_by("-id"):
            rows.append([
                a.batch.name, a.title,
                a.deadline.strftime("%Y-%m-%d %H:%M") if a.deadline else "",
                os.path.basename(a.file.name) if a.file.name else "",
                a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "",
            ])
        return rows

    @admin.action(description="导出 Excel（选中作业）")
    def export_selected_xlsx(self, request, queryset):
        return export_xlsx_response(
            self.ASSIGNMENT_HEADERS, self._assignment_rows(queryset),
            "fvil_assignments_selected.xlsx",
        )


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
    actions = ["bulk_download_source", "export_selected_xlsx"]
    change_list_template = "admin/export_all_change_list.html"

    SUBMISSION_HEADERS = ["作业", "学号", "姓名", "报告文件", "源代码文件", "提交时间", "评分"]

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
        """独立按钮：一键导出全部作业提交。"""
        if not request.user.has_perm("doclib.change_submission"):
            raise PermissionDenied
        return export_xlsx_response(
            self.SUBMISSION_HEADERS, self._submission_rows(Submission.objects.all()),
            "fvil_submissions_all.xlsx",
        )

    def _submission_rows(self, qs):
        rows = []
        for s in qs.select_related("assignment__batch", "applicant").order_by(
            "assignment_id", "student_id"
        ):
            grade = ""
            if s.applicant_id and s.assignment.round_id:
                grade = (
                    Score.objects.filter(
                        applicant_id=s.applicant_id, round_id=s.assignment.round_id
                    ).values_list("grade", flat=True).first()
                ) or ""
            rows.append([
                s.assignment.title, s.student_id, s.name,
                os.path.basename(s.report.name), os.path.basename(s.source.name),
                s.submitted_at.strftime("%Y-%m-%d %H:%M") if s.submitted_at else "",
                grade,
            ])
        return rows

    @admin.action(description="导出 Excel（选中提交）")
    def export_selected_xlsx(self, request, queryset):
        return export_xlsx_response(
            self.SUBMISSION_HEADERS, self._submission_rows(queryset),
            "fvil_submissions_selected.xlsx",
        )

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
    actions = ["export_selected_xlsx"]
    change_list_template = "admin/export_all_change_list.html"

    DOCUMENT_HEADERS = ["标题", "分类", "文件", "上传人", "上传时间"]

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
        """独立按钮：一键导出全部材料。"""
        if not request.user.has_perm("doclib.change_document"):
            raise PermissionDenied
        return export_xlsx_response(
            self.DOCUMENT_HEADERS, self._document_rows(Document.objects.all()),
            "fvil_documents_all.xlsx",
        )

    def _document_rows(self, qs):
        rows = []
        for d in qs.select_related("uploader").order_by("-id"):
            rows.append([
                d.title, d.get_category_display(),
                os.path.basename(d.file.name) if d.file.name else "",
                d.uploader.username if d.uploader else "",
                d.uploaded_at.strftime("%Y-%m-%d %H:%M") if d.uploaded_at else "",
            ])
        return rows

    @admin.action(description="导出 Excel（选中材料）")
    def export_selected_xlsx(self, request, queryset):
        return export_xlsx_response(
            self.DOCUMENT_HEADERS, self._document_rows(queryset),
            "fvil_documents_selected.xlsx",
        )

    def save_model(self, request, obj, form, change):
        """上传材料时自动记录上传人。"""
        if not obj.uploader_id:
            obj.uploader = request.user
        super().save_model(request, obj, form, change)

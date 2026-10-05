from django.core.validators import FileExtensionValidator
from django.db import models

from recruitment.models import Applicant, Batch, Round


class Assignment(models.Model):
    """作业：发布 PDF 文件供下载；自动关联 homework 轮次（T3-5）用于批改录分进 Score。"""

    batch = models.ForeignKey(
        Batch, verbose_name="招新批次", on_delete=models.CASCADE, related_name="assignments"
    )
    round = models.ForeignKey(
        Round, verbose_name="关联轮次", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="保存时自动创建/复用（round_type=homework），用于批改录分",
    )
    title = models.CharField("标题", max_length=100)
    description = models.TextField("说明", blank=True, help_text="作业要求、需提交的材料等")
    file = models.FileField(
        "作业文件（PDF）", upload_to="doclib/assignments/",
        validators=[FileExtensionValidator(["pdf"])],
    )
    deadline = models.DateTimeField("截止时间", null=True, blank=True)
    created_at = models.DateTimeField("发布时间", auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "作业"
        verbose_name_plural = "作业"

    def save(self, *args, **kwargs):
        if self.round_id is None and self.batch_id:
            self.round, _ = Round.objects.get_or_create(
                batch=self.batch, name=self.title, defaults={"round_type": "homework"}
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch.name} · {self.title}"


class Submission(models.Model):
    """作业提交：report.pdf（报告，独立文件、可预览）+ source.zip（源代码）同一次提交；
    身份 = 学号 + 姓名，校验"已在报名库"；同一作业同一学号仅一份。"""

    assignment = models.ForeignKey(
        Assignment, verbose_name="作业", on_delete=models.CASCADE, related_name="submissions"
    )
    applicant = models.ForeignKey(
        Applicant, verbose_name="报名者", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="提交时按学号+姓名匹配报名库自动关联，用于批改录分",
    )
    student_id = models.CharField("学号", max_length=20)
    name = models.CharField("姓名", max_length=30)
    report = models.FileField(
        "报告（PDF）", upload_to="doclib/submissions/report/",
        validators=[FileExtensionValidator(["pdf"])],
    )
    source = models.FileField(
        "源代码（ZIP）", upload_to="doclib/submissions/source/",
        validators=[FileExtensionValidator(["zip"])],
    )
    submitted_at = models.DateTimeField("提交时间", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student_id"], name="unique_assignment_student"),
        ]
        ordering = ["-submitted_at"]
        verbose_name = "作业提交"
        verbose_name_plural = "作业提交"

    def __str__(self):
        return f"{self.name}({self.student_id}) · {self.assignment.title}"


class Document(models.Model):
    """导学材料（双形态之"文档材料"）：管理员后台上传 PDF / 代码 ZIP，分类展示、公开下载。"""

    CATEGORY_CHOICES = [
        ("guide", "导学材料"),
        ("homework", "作业文件"),
        ("appendix", "附录"),
        ("other", "其他"),
    ]

    title = models.CharField("标题", max_length=100)
    category = models.CharField("分类", max_length=20, choices=CATEGORY_CHOICES, default="guide")
    description = models.TextField("说明", blank=True)
    file = models.FileField(
        "文件（PDF 或 ZIP）", upload_to="doclib/documents/",
        validators=[FileExtensionValidator(["pdf", "zip"])],
    )
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)
    uploader = models.ForeignKey(
        "auth.User", verbose_name="上传人", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["category", "-id"]
        verbose_name = "资料文档"
        verbose_name_plural = "资料文档"

    def __str__(self):
        return self.title

    @property
    def file_size_display(self):
        """文件大小（人性化显示，列表页用）。"""
        try:
            size = self.file.size
        except (OSError, ValueError):
            return ""
        if size >= 1024 * 1024:
            return f"{size / 1024 / 1024:.1f} MB"
        return f"{size / 1024:.0f} KB"

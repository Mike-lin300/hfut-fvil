import re

from django import forms
from django.utils import timezone

from recruitment.models import Applicant
from .models import Submission

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 单文件 20MB 上限（不传大型资料）

# 命名模板：学号_姓名_report.pdf / 学号_姓名_source.zip
NAME_RE = re.compile(r"^(?P<sid>\d+)_(?P<name>.+?)_(?P<kind>report|source)\.(?P<ext>pdf|zip)$")


class SubmissionForm(forms.ModelForm):
    """作业提交表单：学号+姓名（校验报名库）+ report.pdf + source.zip（类型/命名/大小校验）。"""

    class Meta:
        model = Submission
        fields = ["student_id", "name", "report", "source"]
        labels = {
            "student_id": "学号",
            "name": "姓名",
            "report": "报告（PDF）",
            "source": "源代码（ZIP）",
        }
        widgets = {
            "student_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的学号"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的姓名"}),
            "report": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf"}),
            "source": forms.FileInput(attrs={"class": "form-control", "accept": ".zip"}),
        }
        help_texts = {
            "report": "命名：学号_姓名_report.pdf",
            "source": "命名：学号_姓名_source.zip",
        }

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        self.replaced = False  # save() 后为 True 表示本次是覆盖上次提交

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"].strip()
        if not sid.isdigit() or len(sid) != 10:
            raise forms.ValidationError("请输入正确的学号格式")
        return sid

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_report(self):
        return self._check_file("report", "pdf")

    def clean_source(self):
        return self._check_file("source", "zip")

    def _check_file(self, field, ext):
        f = self.cleaned_data.get(field)
        if not f:
            return f
        if f.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(f"文件超过 {MAX_UPLOAD_SIZE // 1024 // 1024}MB 限制")
        if not f.name.lower().endswith(f".{ext}"):
            raise forms.ValidationError(f"仅接受 {ext.upper()} 文件")
        return f

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        sid = cleaned.get("student_id")
        name = cleaned.get("name")
        report = cleaned.get("report")
        source = cleaned.get("source")

        # 1) 校验"已在报名库"（学号 + 姓名）
        if not Applicant.objects.filter(student_id=sid, name=name).exists():
            self.add_error(None, "该学号/姓名不在报名库中，请确认报名信息。")
            return cleaned

        # 2) 文件命名模板 + 与表单一致性（报告/源代码位置严格区分）
        for field, f in (("report", report), ("source", source)):
            if f is None:
                continue
            m = NAME_RE.match(f.name)
            if not m:
                self.add_error(field, "文件命名不符合要求（应为 学号_姓名_report.pdf / 学号_姓名_source.zip）")
                continue
            if m.group("sid") != sid or m.group("name") != name:
                self.add_error(field, "文件名中的学号/姓名必须与表单填写一致")
            expect = "report" if field == "report" else "source"
            if m.group("kind") != expect:
                self.add_error(field, f"报告与源代码文件放反了：{field} 应命名为 …_{expect}.…")

        return cleaned

    def save(self, commit=True):
        sid = self.cleaned_data["student_id"]
        name = self.cleaned_data["name"]
        applicant = Applicant.objects.filter(student_id=sid, name=name).first()
        existing = None
        if self.assignment:
            existing = Submission.objects.filter(
                assignment=self.assignment, student_id=sid
            ).first()

        if existing is not None:
            # 覆盖写入：替换两份文件（旧文件删除防堆积）、提交时间更新为本次
            self.replaced = True
            sub = existing
            sub.applicant = applicant
            sub.name = name
            sub.report.delete(save=False)
            sub.source.delete(save=False)
            sub.report = self.cleaned_data["report"]
            sub.source = self.cleaned_data["source"]
            sub.submitted_at = timezone.now()
            if commit:
                sub.save()
            return sub

        sub = super().save(commit=False)
        sub.assignment = self.assignment
        sub.applicant = applicant
        if commit:
            sub.save()
        return sub

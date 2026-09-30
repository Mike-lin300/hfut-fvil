from django import forms

from .models import Applicant


class SignupForm(forms.ModelForm):
    """报名表单：姓名/学号/年级/专业/联系方式；不收集意向方向；学号唯一校验。"""

    class Meta:
        model = Applicant
        fields = ["name", "student_id", "grade", "major", "contact"]
        labels = {
            "name": "姓名",
            "student_id": "学号",
            "grade": "年级",
            "major": "专业",
            "contact": "联系方式",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的姓名"}),
            "student_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "10 位学号"}),
            "grade": forms.TextInput(attrs={"class": "form-control", "placeholder": "如 2026"}),
            "major": forms.TextInput(attrs={"class": "form-control", "placeholder": "如 计算机科学与技术"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "选填，推荐 QQ"}),
        }
        help_texts = {"contact": "选填，方便实验室联系你"}

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"].strip()
        if Applicant.objects.filter(student_id=sid).exists():
            raise forms.ValidationError("该学号已报名，请勿重复提交。")
        return sid

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def save(self, batch, commit=True):
        applicant = super().save(commit=False)
        applicant.batch = batch
        if commit:
            applicant.save()
        return applicant


class QueryForm(forms.Form):
    """匿名成绩查询：学号 + 姓名。"""

    student_id = forms.CharField(
        label="学号",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "10 位学号"}),
    )
    name = forms.CharField(
        label="姓名",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "你的姓名"}),
    )

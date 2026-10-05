from django import forms

from .models import Applicant

# 专业选择列表：合肥工业大学宣城校区招生专业
# 来源：2025/2026 年招生计划（掌上高考招生计划库），含物理类 16 个 + 历史类 2 个（网络与新媒体、英语）；
# 与安徽 2025 年物理类投放一致，并补全宣城校区历史类专业。按拼音首字母排序。
MAJOR_CHOICES = [
    ("材料成型及控制工程", "材料成型及控制工程"),
    ("地球信息科学与技术", "地球信息科学与技术"),
    ("电气工程与智能控制", "电气工程与智能控制"),
    ("过程装备与控制工程", "过程装备与控制工程"),
    ("环境工程", "环境工程"),
    ("机械工程", "机械工程"),
    ("经济学", "经济学"),
    ("能源化学工程", "能源化学工程"),
    ("软件工程", "软件工程"),
    ("生物技术", "生物技术"),
    ("食品营养与健康", "食品营养与健康"),
    ("水利水电工程", "水利水电工程"),
    ("土木工程", "土木工程"),
    ("网络与新媒体", "网络与新媒体"),
    ("物流管理（数智物流）", "物流管理（数智物流）"),
    ("新能源材料与器件", "新能源材料与器件"),
    ("英语", "英语"),
    ("智能科学与技术", "智能科学与技术"),
]


class SignupForm(forms.ModelForm):
    """报名表单：姓名/学号/专业（下拉选择）/QQ号；不收集意向方向；学号唯一校验。"""

    major = forms.ChoiceField(
        label="专业",
        choices=MAJOR_CHOICES,
        # size=6：原生 select 弹出层高度无法用 CSS 限制，改为固定 6 行列表框，
        # 超长时滚轮 / 滚动条滚动，避免 18 个专业撑满整页
        widget=forms.Select(attrs={"class": "form-control", "size": "6"}),
    )

    class Meta:
        model = Applicant
        fields = ["name", "student_id", "major", "contact"]
        labels = {
            "name": "姓名",
            "student_id": "学号",
            "major": "专业",
            "contact": "QQ号",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的姓名"}),
            "student_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的学号"}),
            "contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "你的 QQ 号"}),
        }
        help_texts = {"contact": "方便实验室联系你"}

    def clean_contact(self):
        qq = self.cleaned_data["contact"].strip()
        if not qq.isdigit() or not (5 <= len(qq) <= 12):
            raise forms.ValidationError("请输入正确的 QQ 号（5~12 位数字）")
        return qq

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"].strip()
        if not sid.isdigit() or len(sid) != 10:
            raise forms.ValidationError("请输入正确的学号格式")
        if Applicant.objects.filter(student_id=sid).exists():
            raise forms.ValidationError("该学号已报名，请勿重复提交（如有错误，请联系负责人）。")
        return sid

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def save(self, batch, commit=True):
        applicant = super().save(commit=False)
        applicant.batch = batch
        applicant.grade = self.cleaned_data["student_id"][:4]   # 根据学号的特征，年级是前 4 位，可以计算得出
        if commit:
            applicant.save()
        return applicant


class QueryForm(forms.Form):
    """匿名成绩查询：学号 + 姓名。"""

    student_id = forms.CharField(
        label="学号",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "你的学号"}),
    )
    name = forms.CharField(
        label="姓名",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "你的姓名"}),
    )

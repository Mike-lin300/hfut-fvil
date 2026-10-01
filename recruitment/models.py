from django.db import models


class Batch(models.Model):
    """招新批次：每年一届；状态自动拦截报名（T2-4 用）。"""

    STATUS_CHOICES = [
        ("pending", "未开始"),
        ("open", "报名中"),
        ("training", "培训中"),
        ("assessing", "考核中"),
        ("closed", "已结束"),
    ]

    name = models.CharField("批次名称", max_length=50)
    signup_start = models.DateTimeField("报名开始时间", null=True, blank=True)
    signup_end = models.DateTimeField("报名截止时间", null=True, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="pending")
    note = models.TextField("说明", blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "招新批次"
        verbose_name_plural = "招新批次"

    def __str__(self):
        return self.name


class Applicant(models.Model):
    """报名者：新生（非正式成员）。学号唯一；不收集意向方向；不注册账号。"""

    STATUS_CHOICES = [
        ("signed", "已报名"),
        ("training", "培训中"),
        ("passed", "通过"),
        ("failed", "淘汰"),
        ("waitlist", "候补"),
    ]

    name = models.CharField("姓名", max_length=30)
    student_id = models.CharField("学号", max_length=20, unique=True)
    sid = models.PositiveIntegerField("学生编号", unique=True)
    grade = models.CharField("年级", max_length=10)
    major = models.CharField("专业", max_length=50)
    contact = models.CharField("联系方式", max_length=50, blank=True)
    batch = models.ForeignKey(
        Batch, verbose_name="批次", on_delete=models.CASCADE, related_name="applicants"
    )
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="signed")
    signup_time = models.DateTimeField("报名时间", auto_now_add=True)
    remark = models.TextField("备注", blank=True)

    class Meta:
        ordering = ["-signup_time"]
        verbose_name = "报名者"
        verbose_name_plural = "报名者"

    def save(self, *args, **kwargs):
        """新建时自动分配学生编号 sid（从 1 连续自增，管理用；学号仍为 student_id）。"""
        if self.sid is None:
            last = Applicant.objects.order_by("-sid").first()
            self.sid = (last.sid if last else 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}({self.student_id})"


class Round(models.Model):
    """考核轮次：一届可多轮（培训/考核/作业）。"""

    TYPE_CHOICES = [
        ("training", "培训"),
        ("assessment", "考核"),
        ("homework", "作业"),
    ]

    batch = models.ForeignKey(
        Batch, verbose_name="批次", on_delete=models.CASCADE, related_name="rounds"
    )
    name = models.CharField("轮次名称", max_length=50)
    round_type = models.CharField("类型", max_length=20, choices=TYPE_CHOICES, default="training")
    date = models.DateField("日期", null=True, blank=True)
    note = models.TextField("说明", blank=True)

    class Meta:
        ordering = ["batch", "id"]
        verbose_name = "考核轮次"
        verbose_name_plural = "考核轮次"

    def __str__(self):
        return f"{self.batch.name} · {self.name}"


class Score(models.Model):
    """成绩：等级制（A+~B-）+ 可选验收评价；同一报名者同一轮次仅一条（唯一约束）。"""

    GRADE_CHOICES = [
        ("A+", "A+"),
        ("A", "A"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B", "B"),
        ("B-", "B-"),
    ]

    applicant = models.ForeignKey(
        Applicant, verbose_name="报名者", on_delete=models.CASCADE, related_name="scores"
    )
    round = models.ForeignKey(
        Round, verbose_name="轮次", on_delete=models.CASCADE, related_name="scores"
    )
    grade = models.CharField("等级", max_length=2, choices=GRADE_CHOICES)
    comment = models.TextField("评价", blank=True, help_text="验收人员的文本评价，可选")
    entered_by = models.ForeignKey(
        "auth.User", verbose_name="录入人", null=True, blank=True, on_delete=models.SET_NULL
    )
    entered_at = models.DateTimeField("录入时间", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["applicant", "round"], name="unique_applicant_round"),
        ]
        ordering = ["applicant", "round"]
        verbose_name = "成绩"
        verbose_name_plural = "成绩"

    def __str__(self):
        return f"{self.applicant} · {self.round} · {self.grade}"

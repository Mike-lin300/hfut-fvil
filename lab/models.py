from django.db import models


class LabProfile(models.Model):
    """实验室概况（单例使用：后台只维护一条记录，视图取第一条）。"""

    slogan = models.CharField(
        "口号", max_length=100, blank=True,
        help_text="主页 hero 展示的一句话标语",
    )
    intro = models.TextField(
        "简介", help_text="概况页全文，主页摘要自动截断",
    )
    founded_year = models.PositiveIntegerField(
        "成立年份", default=2017,
    )
    contact = models.CharField(
        "联系方式", max_length=200, blank=True,
        help_text="QQ群 / 邮箱等，展示于页脚与概况页",
    )

    class Meta:
        verbose_name = "实验室概况"
        verbose_name_plural = "实验室概况"

    def __str__(self):
        return "实验室概况"


class Teacher(models.Model):
    """指导老师。"""

    name = models.CharField("姓名", max_length=50)
    title = models.CharField(
        "头衔", max_length=100, blank=True,
        help_text="如：教授 / 副教授 / 硕导",
    )
    research = models.CharField(
        "研究方向", max_length=200, blank=True,
    )
    bio = models.TextField("简介", blank=True)
    photo = models.ImageField(
        "照片", upload_to="teachers/", blank=True, null=True,
    )
    order = models.PositiveIntegerField(
        "排序", default=0, help_text="越小越靠前",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "指导老师"
        verbose_name_plural = "指导老师"

    def __str__(self):
        return self.name

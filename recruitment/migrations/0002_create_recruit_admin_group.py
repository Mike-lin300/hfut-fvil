"""数据迁移：创建「招新管理员」用户组并授予 recruitment 四个模型的全部权限。

- 组成员：招新季负责报名/轮次/成绩管理的协管学生（≤20 人），由超级管理员在后台分配；
- 权限范围：recruitment_batch / applicant / round / score 的增删改查（16 项）；
- 非本组成员无法在后台管理招新数据（T2-7 导出页同样校验本组）。
"""

from django.db import migrations


def create_recruit_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    group, _ = Group.objects.get_or_create(name="招新管理员")
    cts = ContentType.objects.filter(
        app_label="recruitment",
        model__in=["batch", "applicant", "round", "score"],
    )
    perms = Permission.objects.filter(content_type__in=cts)
    group.permissions.set(list(perms))


def remove_recruit_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="招新管理员").delete()


class Migration(migrations.Migration):
    dependencies = [("recruitment", "0001_initial")]

    operations = [
        migrations.RunPython(create_recruit_admin_group, remove_recruit_admin_group),
    ]

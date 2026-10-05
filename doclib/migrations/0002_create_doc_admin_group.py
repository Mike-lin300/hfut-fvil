"""数据迁移：创建「资料管理员」用户组并授予 doclib 三个模型的全部权限。

- 组成员：负责发布作业、上传导学材料、管理提交的协管学生，由超级管理员在后台分配；
- 权限范围：doclib_assignment / submission / document 的增删改查（12 项）；
- 非本组成员无法在后台管理 doclib 数据（前台浏览/下载/提交不受限）。
"""

from django.db import migrations


def create_doc_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    group, _ = Group.objects.get_or_create(name="资料管理员")
    cts = ContentType.objects.filter(
        app_label="doclib",
        model__in=["assignment", "submission", "document"],
    )
    perms = Permission.objects.filter(content_type__in=cts)
    group.permissions.set(list(perms))


def remove_doc_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="资料管理员").delete()


class Migration(migrations.Migration):
    dependencies = [("doclib", "0001_initial")]

    operations = [
        migrations.RunPython(create_doc_admin_group, remove_doc_admin_group),
    ]

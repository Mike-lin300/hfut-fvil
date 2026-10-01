# Data migration: T3-0 回填现有报名者的学生编号 sid（按 id 升序 1..N）
# 反转：sid 置回 NULL（保留原 AutoField 主键 id 不变）。

from django.db import migrations


def backfill_sid(apps, schema_editor):
    Applicant = apps.get_model("recruitment", "Applicant")
    n = 0
    for pk in Applicant.objects.order_by("id").values_list("pk", flat=True):
        n += 1
        Applicant.objects.filter(pk=pk).update(sid=n)


def unbackfill_sid(apps, schema_editor):
    Applicant = apps.get_model("recruitment", "Applicant")
    Applicant.objects.update(sid=None)


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0003_applicant_sid_alter_applicant_grade"),
    ]

    operations = [
        migrations.RunPython(backfill_sid, unbackfill_sid),
    ]

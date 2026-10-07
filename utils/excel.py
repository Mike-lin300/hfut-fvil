"""通用 Excel 导出工具：各模型 Admin 的「导出选中/导出全部」动作共用。"""

import openpyxl
from django.http import HttpResponse

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def export_xlsx_response(headers, rows, filename):
    """把表头 + 行数据导出为 .xlsx 下载响应（filename 建议用 ASCII，避免中文头编码问题）。"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(headers)
    for row in rows:
        ws.append(row)
    resp = HttpResponse(content_type=XLSX_MIME)
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp

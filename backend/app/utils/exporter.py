"""Excel export helpers (openpyxl)."""
from __future__ import annotations

import io
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


def export_rows(headers: list[str], rows: list[list[Any]], title: str = "Report") -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1E40AF")
        cell.alignment = Alignment(horizontal="center")
    for r in rows:
        ws.append(r)
    ws.freeze_panes = "A2"
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def export_dicts(headers: list[str], dicts: list[dict], keys: list[str], title: str = "Report") -> bytes:
    rows = [[d.get(k, "") for k in keys] for d in dicts]
    return export_rows(headers, rows, title)

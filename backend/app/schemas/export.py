"""
export.py — Pydantic v2 schemas for export requests.
"""
from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    """Supported export formats."""
    md = "md"
    txt = "txt"
    pdf = "pdf"
    docx = "docx"
    zip = "zip"


class ExportRequest(BaseModel):
    """Schema for export request."""
    format: ExportFormat = ExportFormat.md

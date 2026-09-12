"""PDF report export routes."""

import re

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import factory_service, report_service

router = APIRouter(prefix="/api/report", tags=["report"])


def _slugify(name: str) -> str:
    """Sanitize a factory name for safe use in a Content-Disposition filename."""

    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")
    return slug or "factory"


@router.get("/factory/{factory_id}")
def get_factory_report(factory_id: int, db: Session = Depends(get_db)) -> Response:
    pdf_bytes = report_service.generate_report_pdf(db, factory_id)
    factory = factory_service.get(db, factory_id)
    filename = f"{_slugify(factory.name)}-carbon-report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

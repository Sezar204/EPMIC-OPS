from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok, fail
from app.utils.importer import DataImporter
from app.utils.exporter import export_dicts

router = APIRouter()
_importer = DataImporter()


@router.post("/excel/{factory_id}/{entity}")
async def import_excel(factory_id: int, entity: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    result = _importer.import_and_validate(factory_id, entity, content)
    return ok(result, "Validation complete")


@router.post("/excel/{factory_id}/{entity}/commit")
async def commit_excel(factory_id: int, entity: str, payload: dict, db: Session = Depends(get_db)):
    result = _importer.commit_import(factory_id, entity, payload.get("rows", []))
    return ok(result, "Import committed")


@router.get("/template/{entity}")
def template(entity: str, db: Session = Depends(get_db)):
    try:
        data = _importer.generate_template(entity)
    except ValueError:
        return fail("Unsupported entity")
    from fastapi.responses import Response
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename={entity}_template.xlsx"})


@router.post("/export/{factory_id}/{entity}")
def export_entity(factory_id: int, entity: str, db: Session = Depends(get_db)):
    return ok({"message": "Use reports generate + client export"}, "OK")

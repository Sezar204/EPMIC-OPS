Input
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.utils.importer import DataImporter, ENTITY_TEMPLATES
from app.utils.exporter import to_excel

router = APIRouter()
importer = DataImporter()


@router.post("/excel/{factory_id}/{entity}")
async def import_excel(factory_id: int, entity: str,
                       file: UploadFile = File(...),
                       db: Session = Depends(get_db)):
    if entity not in ENTITY_TEMPLATES:
        raise HTTPException(400, f"Unknown entity: {entity}")
    content = await file.read()
    result = importer.import_and_validate(content, entity)
    return ok(result)


@router.get("/template/{entity}")
def get_template(entity: str):
    if entity not in ENTITY_TEMPLATES:
        raise HTTPException(400, f"Unknown entity: {entity}")
    data = importer.generate_template(entity)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={entity}_template.xlsx"},
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dataset import Dataset


router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["Datasets"],
)


@router.get("/")
def get_datasets(
    db: Session = Depends(get_db),
):
    return (
        db.query(Dataset)
        .order_by(Dataset.created_at.desc())
        .all()
    )
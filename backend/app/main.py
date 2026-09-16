from fastapi import FastAPI

from app.database import Base, engine

from app.models.dataset import Dataset
from app.models.observation import ClimateObservation

from app.api.datasets import router as datasets_router
from app.api.observations import router as observations_router

from app.routers import locations

app = FastAPI(
    title="AI-Powered Digital Twin of India",
    description=(
        "National-scale climate data integration "
        "and digital twin backend."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(
        bind=engine
    )


app.include_router(
    datasets_router
)

app.include_router(
    observations_router
)

app.include_router(
    locations.router
)

@app.get("/")
def root():
    return {
        "name": "AI-Powered Digital Twin of India",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
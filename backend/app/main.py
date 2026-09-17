from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

from app.models.dataset import Dataset
from app.models.observation import ClimateObservation
from app.models.rainfall import RainfallObservation

from app.api.datasets import router as datasets_router
from app.api.observations import router as observations_router
from app.routers.map import router as map_router
from app.routers import locations
from app.routers import timeseries
from app.routers import metrics
from app.routers import map
from app.routers.rainfall import router as rainfall_router

app = FastAPI(
    title="AI-Powered Digital Twin of India",
    description=(
        "National-scale climate data integration "
        "and digital twin backend."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    timeseries.router
)

app.include_router(
    metrics.router
)

app.include_router(
    map.router
)

app.include_router(map_router)

app.include_router(rainfall_router)

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
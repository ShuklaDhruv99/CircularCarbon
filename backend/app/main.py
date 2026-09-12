"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    action_plan,
    emissions,
    energy,
    explanations,
    factories,
    health,
    materials,
    processes,
    recommendations,
    simulations,
    waste,
)
from app.core.config import settings
from app.services.errors import NotFoundError, ValidationError

app = FastAPI(title="CircularCarbon AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
def handle_not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ValidationError)
def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


app.include_router(health.router)
app.include_router(factories.router)
app.include_router(processes.router)
app.include_router(energy.router)
app.include_router(materials.router)
app.include_router(waste.router)
app.include_router(emissions.router)
app.include_router(recommendations.router)
app.include_router(explanations.router)
app.include_router(simulations.router)
app.include_router(action_plan.router)

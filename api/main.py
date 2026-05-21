from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.predict import router as predict_router
from api.routes.simulate import router as simulate_router
from api.routes.forecast import router as forecast_router
from api.routes.explain import router as explain_router

app = FastAPI(
    title="MedTwin AI",
    description="Healthcare Digital Twin — Disease Progression Prediction API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    predict_router,
    prefix="/api/v1",
    tags=["Risk Prediction"]
)

app.include_router(
    simulate_router,
    prefix="/api/v1",
    tags=["Simulation"]
)

app.include_router(
    forecast_router,
    prefix="/api/v1",
    tags=["Forecasting"]
)

app.include_router(
    explain_router,
    prefix="/api/v1",
    tags=["Explainability"]
)


@app.get("/")
def root():
    return {
        "message": "MedTwin AI is running",
        "docs": "/docs"
    }
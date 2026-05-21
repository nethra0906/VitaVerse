from fastapi import APIRouter
from api.schemas import ForecastInput
from src.simulation.digital_twin import DigitalTwin

router = APIRouter()
twin   = DigitalTwin()


@router.post("/forecast")
def forecast(body: ForecastInput):
    result = twin.forecast_biomarkers(body.patient.dict(), months=body.months)
    return {"status": "success", "data": result}
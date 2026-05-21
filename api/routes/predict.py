from fastapi import APIRouter
from api.schemas import PatientInput
from src.simulation.digital_twin import DigitalTwin

router = APIRouter()
twin   = DigitalTwin()


@router.post("/risk")
def predict_risk(patient: PatientInput):
    result = twin.predict_risk(patient.dict())
    return {"status": "success", "data": result}
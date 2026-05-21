from fastapi import APIRouter
from api.schemas import InterventionInput
from src.simulation.digital_twin import DigitalTwin

router = APIRouter()
twin   = DigitalTwin()


@router.post("/simulate")
def simulate_intervention(body: InterventionInput):
    result = twin.simulate_intervention(body.patient.dict(), body.interventions)
    return {"status": "success", "data": result}
from fastapi import APIRouter
from api.schemas import PatientInput
from src.explainability.shap_explainer import explain_prediction

router = APIRouter()


@router.post("/explain")
def explain(patient: PatientInput):
    result = explain_prediction(patient.dict())
    return {"status": "success", "data": result}
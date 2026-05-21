from pydantic import BaseModel, Field
from typing import Optional, Dict


class PatientInput(BaseModel):
    Age:              float = Field(..., example=45)
    Gender:           int   = Field(..., example=1)       # 0=F, 1=M
    BMI:              float = Field(..., example=31.0)
    Glucose:          float = Field(..., example=155.0)
    BloodPressure:    float = Field(..., example=130.0)
    HbA1c:            float = Field(..., example=8.2)
    Cholesterol:      float = Field(..., example=240.0)
    Insulin:          float = Field(..., example=120.0)
    Exercise_min_day: float = Field(..., example=10.0)
    Smoking:          int   = Field(..., example=1)
    Alcohol:          int   = Field(..., example=0)
    SleepHours:       float = Field(..., example=5.5)
    MedAdherence:     float = Field(..., example=0.6)


class InterventionInput(BaseModel):
    patient:       PatientInput
    interventions: Dict[str, float] = Field(
        ...,
        example={"Exercise_min_day": 45, "Smoking": 0, "MedAdherence": 0.95}
    )


class ForecastInput(BaseModel):
    patient: PatientInput
    months:  int = Field(default=12, ge=1, le=60)
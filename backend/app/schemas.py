from pydantic import BaseModel, Field
from typing import Optional, List

class SinglePredictRequest(BaseModel):
    smiles: str = Field(..., min_length=1)
    active_site_residues: str = Field(..., min_length=27, max_length=27)

class SinglePredictResponse(BaseModel):
    model_name: str
    smiles: str
    active_site_residues: str
    final_score: float
    status: str

class BatchPredictRow(BaseModel):
    smiles: str
    active_site_residues: str
    final_score: float
    status: str

class BatchPredictResponse(BaseModel):
    model_name: str
    total_rows: int
    success_rows: int
    failed_rows: int
    predictions: list[BatchPredictRow]

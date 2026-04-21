from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO

from .schemas import SinglePredictRequest
from .model_loader import load_models
from .predict_service import predict_catboost, predict_ensemble
from .csv_service import (
    read_uploaded_csv,
    validate_csv_columns,
    validate_csv_row_limit,
    run_batch_prediction,
    batch_results_to_csv_bytes,
)

app = FastAPI(title="Binding Score Predictor API", version="1.0.0")

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://github.com/Dr-Islam-Lab-Group/ML_binding_score_prediction",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    load_models()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict/catboost")
def single_predict_catboost(request: SinglePredictRequest):
    try:
        return predict_catboost(request.smiles, request.active_site_residues)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict/ensemble")
def single_predict_ensemble(request: SinglePredictRequest):
    try:
        return predict_ensemble(request.smiles, request.active_site_residues)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch/catboost")
async def batch_predict_catboost(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df, max_rows=1000)

        return run_batch_prediction(
            df=df,
            predict_fn=predict_catboost,
            model_name="catboost",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch/ensemble")
async def batch_predict_ensemble(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df, max_rows=1000)

        return run_batch_prediction(
            df=df,
            predict_fn=predict_ensemble,
            model_name="ensemble",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch-download/catboost")
async def batch_predict_download_catboost(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df, max_rows=1000)

        result = run_batch_prediction(
            df=df,
            predict_fn=predict_catboost,
            model_name="catboost",
        )

        csv_bytes = batch_results_to_csv_bytes(result)

        return StreamingResponse(
            BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=catboost_predictions.csv"},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch-download/ensemble")
async def batch_predict_download_ensemble(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df, max_rows=1000)

        result = run_batch_prediction(
            df=df,
            predict_fn=predict_ensemble,
            model_name="ensemble",
        )

        csv_bytes = batch_results_to_csv_bytes(result)

        return StreamingResponse(
            BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=ensemble_predictions.csv"},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

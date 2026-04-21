from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO

from .schemas import SinglePredictRequest
from .model_loader import load_models
from .predict_service import predict
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
    "https://YOUR_GITHUB_USERNAME.github.io",
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

@app.get("/")
def root():
    return {"message": "Binding Score Predictor API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def single_predict(request: SinglePredictRequest):
    try:
        return predict(request.smiles, request.active_site_residues)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch")
async def batch_predict(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df)

        return run_batch_prediction(
            df=df,
            predict_fn=predict,
            model_name="ensemble",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/predict-batch-download")
async def batch_predict_download(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        df = read_uploaded_csv(file_bytes)
        validate_csv_columns(df)
        validate_csv_row_limit(df)

        result = run_batch_prediction(
            df=df,
            predict_fn=predict,
            model_name="ensemble",
        )

        csv_bytes = batch_results_to_csv_bytes(result)

        return StreamingResponse(
            BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

import pickle
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

catboost_model = None
ensemble_model = None

def load_models():
    global catboost_model, ensemble_model

    with open(MODEL_DIR / "catboost.pkl", "rb") as f:
        catboost_model = pickle.load(f)

    with open(MODEL_DIR / "ensemble.pkl", "rb") as f:
        ensemble_model = pickle.load(f)

def get_catboost_model():
    return catboost_model

def get_ensemble_model():
    return ensemble_model

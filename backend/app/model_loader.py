import pickle
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

ensemble_model = None

def load_models():
    global ensemble_model

    with open(MODEL_DIR / "ensemble.pkl", "rb") as f:
        ensemble_model = pickle.load(f)

def get_model():
    return ensemble_model

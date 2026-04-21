import numpy as np
from .model_loader import get_catboost_model, get_ensemble_model
from .preprocess import prepare_single_input
from .validators import validate_smiles, validate_residues

def predict_catboost(smiles: str, active_site_residues: str):
    smiles = validate_smiles(smiles)
    active_site_residues = validate_residues(active_site_residues)

    df = prepare_single_input(smiles, active_site_residues)
    model = get_catboost_model()

    pred = model.predict(df)
    final_score = float(np.ravel(pred)[0])

    return {
        "model_name": "catboost",
        "smiles": smiles,
        "active_site_residues": active_site_residues,
        "final_score": final_score,
        "status": "success"
    }

def predict_ensemble(smiles: str, active_site_residues: str):
    smiles = validate_smiles(smiles)
    active_site_residues = validate_residues(active_site_residues)

    df = prepare_single_input(smiles, active_site_residues)
    model = get_ensemble_model()

    pred = model.predict(df)
    final_score = float(np.ravel(pred)[0])

    return {
        "model_name": "ensemble",
        "smiles": smiles,
        "active_site_residues": active_site_residues,
        "final_score": final_score,
        "status": "success"
    }

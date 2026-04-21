import pandas as pd

def prepare_single_input(smiles: str, active_site_residues: str) -> pd.DataFrame:
    row = {
        "smiles": smiles,
        "active_site_residues": active_site_residues
    }
    df = pd.DataFrame([row])

    # Add your real preprocessing here
    # Example:
    # - descriptor generation from smiles
    # - splitting residues into 27 columns
    # - categorical transforms
    # - scaling if needed

    return df

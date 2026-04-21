VALID_RESIDUES = set("ACDEFGHIKLMNPQRSTVWYBXZJUO")

def validate_smiles(smiles: str) -> str:
    smiles = smiles.strip()
    if not smiles:
        raise ValueError("SMILES cannot be empty")
    return smiles

def validate_residues(residues: str) -> str:
    residues = residues.strip().upper()
    if len(residues) != 27:
        raise ValueError("Active site residue input must be exactly 27 characters")
    if any(ch not in VALID_RESIDUES for ch in residues):
        raise ValueError("Active site residues contain invalid characters")
    return residues

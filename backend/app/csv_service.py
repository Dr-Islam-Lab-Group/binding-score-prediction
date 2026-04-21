from __future__ import annotations

from io import StringIO, BytesIO
from typing import Callable, Dict, Any

import pandas as pd


REQUIRED_COLUMNS = ["smiles", "active_site_residues"]


def read_uploaded_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Read uploaded CSV bytes into a pandas DataFrame.
    """
    try:
        text = file_bytes.decode("utf-8")
        df = pd.read_csv(StringIO(text))
        return df
    except UnicodeDecodeError as exc:
        raise ValueError("CSV file must be UTF-8 encoded.") from exc
    except Exception as exc:
        raise ValueError(f"Could not read CSV file: {exc}") from exc


def validate_csv_columns(df: pd.DataFrame) -> None:
    """
    Ensure the CSV contains the required columns.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(missing)}"
        )


def validate_csv_row_limit(df: pd.DataFrame, max_rows: int = 1000) -> None:
    """
    Prevent very large uploads in the first version.
    """
    if len(df) == 0:
        raise ValueError("CSV file is empty.")
    if len(df) > max_rows:
        raise ValueError(
            f"CSV has {len(df)} rows. Maximum allowed is {max_rows} rows."
        )


def run_batch_prediction(
    df: pd.DataFrame,
    predict_fn: Callable[[str, str], Dict[str, Any]],
    model_name: str,
) -> Dict[str, Any]:
    """
    Apply the given prediction function row by row.
    predict_fn must accept (smiles, active_site_residues).
    """
    results = []

    for _, row in df.iterrows():
        smiles = "" if pd.isna(row.get("smiles")) else str(row.get("smiles")).strip()
        residues = (
            "" if pd.isna(row.get("active_site_residues"))
            else str(row.get("active_site_residues")).strip()
        )

        try:
            result = predict_fn(smiles, residues)
            results.append(result)
        except Exception as exc:
            results.append({
                "model_name": model_name,
                "smiles": smiles,
                "active_site_residues": residues,
                "final_score": None,
                "status": f"failed: {str(exc)}",
            })

    success_rows = sum(r["status"] == "success" for r in results)
    failed_rows = len(results) - success_rows

    return {
        "model_name": model_name,
        "total_rows": len(results),
        "success_rows": success_rows,
        "failed_rows": failed_rows,
        "predictions": results,
    }


def batch_results_to_csv_bytes(batch_result: Dict[str, Any]) -> bytes:
    """
    Convert batch result JSON into downloadable CSV bytes.
    """
    predictions = batch_result.get("predictions", [])
    df = pd.DataFrame(predictions)

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output.read()

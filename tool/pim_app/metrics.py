from __future__ import annotations
import pandas as pd

DEFAULT_YELLOW_COLS = ["Macro Material_", "Main Color_", "Shape_", "Carry_"]

def add_completeness(df: pd.DataFrame,
                     cols: list[str] = DEFAULT_YELLOW_COLS) -> pd.DataFrame:
    """Add a binary 'Complete Status' column based on completeness of given columns."""
    out = df.copy()
    present = [c for c in cols if c in out.columns]
    if not present:
        return out
    out["Complete Status"] = (
        out[present]
        .apply(lambda row: 0 if row.isna().any() or any(str(x).strip() == "" for x in row) else 1, axis=1)
        .astype(int)
    )
    return out

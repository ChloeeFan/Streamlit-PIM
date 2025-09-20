from __future__ import annotations
from io import BytesIO
import json
import pandas as pd
from pandas.errors import ParserError

# columns that should always be treated as text
ID_LIKE_COLS = {"sku", "ean", "upc", "barcode", "url", "image url", "id"}

def _read_with_fallbacks(file_like,
                         sheet_name: str = "PIM",
                         usecols: str | None = None,
                         header: int | None = 1,
                         dtype_map: dict | None = None) -> pd.DataFrame:
    """Try strict settings first, then relax if the Excel file is small or oddly formatted."""
    attempts = [
        dict(sheet_name=sheet_name, usecols=usecols, header=header, dtype=dtype_map),
        dict(sheet_name=sheet_name, usecols=usecols, header=0,      dtype=dtype_map),
        dict(sheet_name=sheet_name, usecols=None,   header=header, dtype=dtype_map),
        dict(sheet_name=sheet_name, usecols=None,   header=0,      dtype=dtype_map),
    ]

    def _seekable(f):
        try:
            f.seek(0)
            return True
        except Exception:
            return False

    for opts in attempts:
        try:
            if isinstance(file_like, (bytes, bytearray)):
                return pd.read_excel(BytesIO(file_like), **opts)
            if _seekable(file_like):
                file_like.seek(0)
            return pd.read_excel(file_like, **opts)
        except (ParserError, ValueError, KeyError):
            continue
        except Exception:
            continue

    # Last resort
    if isinstance(file_like, (bytes, bytearray)):
        return pd.read_excel(BytesIO(file_like))
    if _seekable(file_like):
        file_like.seek(0)
    return pd.read_excel(file_like)

def read_excel_from_bytes(data: bytes,
                          sheet_name: str = "PIM",
                          usecols: str | None = None,
                          header: int | None = 0) -> pd.DataFrame:
    """Read Excel from raw bytes with safe dtype and fallbacks."""
    dtype_map = {"SKU": str, "URL": str, "Image URL": str}
    return _read_with_fallbacks(data, sheet_name=sheet_name, usecols=usecols, header=header, dtype_map=dtype_map)

def read_excel_from_uploaded(uploaded_file,
                             sheet_name: str = "PIM",
                             usecols: str | None = None,
                             header: int | None = 0) -> pd.DataFrame:
    """Read Excel from a Streamlit UploadedFile with safe dtype and fallbacks."""
    dtype_map = {"SKU": str, "URL": str, "Image URL": str}
    return _read_with_fallbacks(uploaded_file, sheet_name=sheet_name, usecols=usecols, header=header, dtype_map=dtype_map)

def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names, drop junk/empty columns, normalize dates."""
    df = df.copy()
    df.columns = df.columns.map(str).str.strip()
    df = df.loc[:, ~df.columns.str.match(r"^Unnamed.*$")]
    df = df.loc[:, df.columns.str.len() > 0]
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.match(r"^\|.*$")]
    df = df.loc[:, ~df.columns.str.match(r"^\d+$")]
    if "Column2" in df.columns:
        df = df.drop(columns=["Column2"])
    if "Added" in df.columns:
        df["Added"] = pd.to_datetime(df["Added"], errors="coerce").dt.strftime("%Y-%m-%d")
    for c in ["Complete?", "Model", "Size"]:
        if c in df.columns:
            df = df.drop(columns=c)
    return df.reset_index(drop=True)

def coerce_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize object columns so Arrow/Streamlit won’t choke on mixed types."""
    out = df.copy()

    # decode bytes
    for col in out.columns:
        if out[col].dtype == "object":
            mask = out[col].map(lambda x: isinstance(x, (bytes, bytearray)))
            if getattr(mask, "any", lambda: False)():
                out.loc[mask, col] = out.loc[mask, col].map(
                    lambda b: b.decode("utf-8", "ignore") if isinstance(b, (bytes, bytearray)) else b
                )

    # stringify list/dict/set
    def _to_text(x):
        if isinstance(x, (list, dict, set)):
            return json.dumps(x, default=str, ensure_ascii=False)
        return x

    for col in out.columns:
        if out[col].dtype == "object":
            out[col] = out[col].map(_to_text)

    # enforce string dtype on id-like columns
    for col in out.columns:
        if col.lower() in ID_LIKE_COLS:
            out[col] = out[col].astype("string").fillna("")

    # any remaining mixed-type object → string
    for col in out.columns:
        if out[col].dtype == "object" and out[col].map(type).nunique() > 1:
            out[col] = out[col].astype("string").fillna("")

    return out

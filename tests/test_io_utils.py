import pandas as pd
from io import BytesIO
from pim_app.io_utils import read_excel_from_bytes, process_dataframe, coerce_text_columns


def make_excel_bytes(df: pd.DataFrame) -> bytes:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="PIM")
    bio.seek(0)
    return bio.read()

def test_read_excel_from_bytes_dtype_string():
    raw = make_excel_bytes(pd.DataFrame({"SKU": [123, "ABC"], "URL": ["http://x", None], "Image URL": [None, "http://y"]}))
    df = read_excel_from_bytes(raw)
    assert df["SKU"].dtype == object or str(df["SKU"].dtype).startswith("string")

def test_process_dataframe_basic_cleanup():
    df = pd.DataFrame({" Unnamed: 0": [1], "Added": ["2024-01-02"], "Model": ["X"]})
    df = process_dataframe(df)
    assert "Unnamed: 0" not in df.columns
    assert "Model" not in df.columns
    assert "Added" in df.columns
    assert df["Added"].iloc[0] == "2024-01-02"

def test_coerce_text_columns_mixed_types():
    df = pd.DataFrame({"SKU": [b"12", 34, "56"], "desc": ["a", {"k":"v"}, ["x","y"]]})
    out = coerce_text_columns(df)
    assert str(out["SKU"].dtype).startswith("string")
    assert out["desc"].dtype == object or str(out["desc"].dtype).startswith("string")

import pandas as pd
from pim_app.metrics import add_completeness

def test_add_completeness():
    df = pd.DataFrame({
        "Macro Material_": ["cotton", ""],
        "Main Color_":     ["red",    "blue"],
        "Shape_":          ["round",  "round"],
        "Carry_":          ["hand",   "hand"]
    })
    out = add_completeness(df)
    assert "Complete Status" in out.columns
    assert out["Complete Status"].tolist() == [1, 0]

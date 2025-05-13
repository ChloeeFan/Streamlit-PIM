import streamlit as st
import pandas as pd
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

st.set_page_config(layout="wide")
st.title("250408 PIM Lite Consolidated")

# Excel path and sheet
excel_path = Path("/workspaces/blank-app/250408_PIM Lite Consolidated.xlsx")
sheet_name = "PIM"

if not excel_path.exists():
    st.error(f"❌ File not found: {excel_path}")
else:
    @st.cache_data
    def load_data():
        df = pd.read_excel(
            excel_path,
            sheet_name=sheet_name,
            usecols="A:U",
            header=1
        )

        # Clean column names
        df.columns = df.columns.map(str).str.strip()

        # Drop unwanted/ghost/empty columns
        df = df.loc[:, ~df.columns.str.match(r'^Unnamed.*$')]
        df = df.loc[:, df.columns.str.len() > 0]
        df = df.dropna(axis=1, how="all")
        df = df.loc[:, ~df.columns.str.match(r'^\|.*$')]
        df = df.loc[:, ~df.columns.str.match(r'^\d+$')]

        return df

    df = load_data()

    if "Column2" in df.columns:
        df = df.drop(columns=["Column2"])

    if "Added" in df.columns:
        df["Added"] = pd.to_datetime(df["Added"], errors="coerce").dt.strftime("%d/%m/%Y")

    # Drop extra columns you want to remove
    cols_to_drop = ["Complete?", "Model", "Size"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Yellow-highlighted columns
    yellow_highlight_cols = ["Macro Material_", "Main Color_", "Shape_", "Carry_"]

    # ✅ Create 'Complete Status' BEFORE building grid
    df["Complete Status"] = df[yellow_highlight_cols].apply(
        lambda row: all(x and str(x).strip() != "" for x in row), axis=1
    ).astype(int)

    # ✅ JS renderers
    image_renderer = JsCode("""
    class ImgCellRenderer {
        init(params) {
            this.eGui = document.createElement('div');
            if (params.value) {
                this.eGui.innerHTML = `<img src="${params.value}" style="height:60px; object-fit:contain;" />`;
            }
        }
        getGui() {
            return this.eGui;
        }
    }
    """)

    highlight_count = JsCode("""
    function(params) {
        const style = {
            'fontSize': '11px',
            'fontFamily': 'Arial, sans-serif'
        };
        if (parseFloat(params.value) > 1) {
            style.color = 'white';
            style.backgroundColor = 'red';
            style.fontWeight = 'bold';
        }
        return style;
    }
    """)

    highlight_incomplete = JsCode("""
    function(params) {
        const style = {
            'fontSize': '11px',
            'fontFamily': 'Arial, sans-serif'
        };
        if (parseInt(params.value) === 0) {
            style.color = 'white';
            style.backgroundColor = 'red';
            style.fontWeight = 'bold';
        }
        return style;
    }
    """)

    # ✅ Grid builder (after 'Complete Status' added)
    gb = GridOptionsBuilder.from_dataframe(df)

    # Default column styling
    gb.configure_default_column(
        resizable=True,
        filter=True,
        sortable=True,
        editable=True,
        wrapText=True,
        autoHeight=False,
        cellStyle={
            "fontSize": "11px",
            "fontFamily": "Arial, sans-serif",
            "lineHeight": "1.2"
        }
    )

    # Yellow-highlighted columns
    yellow_style = JsCode("""
    function(params) {
        return {
            'backgroundColor': '#fffac8',
            'fontSize': '11px',
            'fontFamily': 'Arial, sans-serif'
        }
    }
    """)
    for col in yellow_highlight_cols:
        if col in df.columns:
            gb.configure_column(col, cellStyle=yellow_style, minWidth=90)

    # Image column (unchanged)
    if "Image URL" in df.columns:
        gb.configure_column("Image URL", cellRenderer=image_renderer, editable=False, width=230)

    # ✅ URL column as editable text (without modification)
    if "URL" in df.columns:
        gb.configure_column("URL", editable=True, width=250)

    # Highlight Count column
    count_col = next((col for col in df.columns if col.strip().lower() == "count"), None)
    if count_col:
        gb.configure_column(count_col, cellStyle=highlight_count)

    # Highlight Complete Status column
    if "Complete Status" in df.columns:
        gb.configure_column("Complete Status", cellStyle=highlight_incomplete, width=120)

    # Key wrapped columns
    wide_wrap_cols = ["Name", "Brand", "Category", "Main Color_"]
    for col in wide_wrap_cols:
        if col in df.columns:
            gb.configure_column(col, wrapText=True, autoHeight=False, minWidth=120)

    # Dropdown columns
    dropdown_cols = ["Macro Material_", "Main Material_", "Main Color_", "Shape_", "Carry_"]
    for col in dropdown_cols:
        if col in df.columns:
            unique_vals = df[col].dropna().astype(str).unique().tolist()
            gb.configure_column(
                col,
                editable=True,
                cellEditor="agSelectCellEditor",
                cellEditorParams={"values": unique_vals},
                wrapText=True,
                autoHeight=False,
                minWidth=100
            )

    # Set row height
    gb.configure_grid_options(rowHeight=60)
    grid_options = gb.build()

    # Header font styling
    custom_css = {
        ".ag-header-cell-label": {
            "font-size": "11px",
            "line-height": "1.2",
            "white-space": "normal"
        }
    }

    # Show AgGrid table
    AgGrid(
        df,
        gridOptions=grid_options,
        height=900,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        enable_enterprise_modules=True,
        theme="alpine",
        fit_columns_on_grid_load=True,
        custom_css=custom_css
    )

import streamlit as st
import pandas as pd
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import warnings

# Suppress the specific warning from openpyxl
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.set_page_config(layout="wide")
st.title("250408 PIM Lite Consolidated")

# Folder where your script and the file will be saved
folder_path = Path(__file__).parent

# Hidden file to store the last uploaded file (the file will be saved with a .hidden extension)
hidden_file_path = folder_path / ".last_uploaded_file.hidden"

# Function to process the dataframe (cleaning and column setups)
def process_dataframe(df):
    # Clean column names
    df.columns = df.columns.map(str).str.strip()

    # Drop unwanted/ghost/empty columns
    df = df.loc[:, ~df.columns.str.match(r'^Unnamed.*$')]
    df = df.loc[:, df.columns.str.len() > 0]
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.match(r'^\|.*$')]
    df = df.loc[:, ~df.columns.str.match(r'^\d+$')]

    if "Column2" in df.columns:
        df = df.drop(columns=["Column2"])

    # Ensure 'Added' column is in datetime format and format it to display only the date
    if "Added" in df.columns:
        df["Added"] = pd.to_datetime(df["Added"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Drop extra columns you want to remove
    cols_to_drop = ["Complete?", "Model", "Size"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    return df

# Stage 1: User Choice
user_choice = st.radio("Choose an option:", ["Open previous file", "Upload new file"])

# Initialize variable for uploaded file
uploaded_file = None

if user_choice == "Open previous file":
    # Check if the hidden file exists
    if hidden_file_path.exists():
        st.info(f"Found a previously uploaded file. Loading...")
        try:
            # Open the hidden file as bytes and load it into a pandas DataFrame
            with open(hidden_file_path, "rb") as f:
                uploaded_file = f.read()  # Read the file as bytes
            
            # Load the file into a pandas dataframe
            from io import BytesIO
            df = pd.read_excel(
    BytesIO(uploaded_file),        # or uploaded_file for the upload branch
    sheet_name="PIM",
    usecols="A:U",
    header=1,
    dtype={"SKU": str, "URL": str, "Image URL": str}  # <— add this
)

            # Process the dataframe (cleaning and column setup)
            df = process_dataframe(df)

            # Your grid configuration logic (highlighting, dropdowns, etc.) remains the same
            yellow_highlight_cols = ["Macro Material_", "Main Color_", "Shape_", "Carry_"]
            df["Complete Status"] = df[yellow_highlight_cols].apply(
                lambda row: 0 if row.isna().any() or any(str(x).strip() == "" for x in row) else 1, axis=1
            ).astype(int)

            # Build grid options
            gb = GridOptionsBuilder.from_dataframe(df)

            # Configure default column behavior
            gb.configure_default_column(
                resizable=True,
                filter=True,
                sortable=True,
                editable=True,
                wrapText=True,
                autoHeight=False,
                cellStyle={"fontSize": "11px", "fontFamily": "Arial, sans-serif", "lineHeight": "1.2"}
            )

            # Add the column configurations for dropdowns, highlights, and custom JS renderers
            yellow_style = JsCode("""
                function(params) {
                    if (params.value == null || params.value.toLowerCase() === "blanket") {
                        return { 'backgroundColor': '#ffcc99', 'fontSize': '11px' };
                    }
                    return { 'backgroundColor': '#fffac8', 'fontSize': '11px' };
                }
            """)

            for col in yellow_highlight_cols:
                if col in df.columns:
                    gb.configure_column(col, cellStyle=yellow_style, minWidth=90)

            # Image rendering for URLs
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

            if "Image URL" in df.columns:
                gb.configure_column("Image URL", cellRenderer=image_renderer, editable=False, width=230)

            # Make URLs clickable
            url_renderer = JsCode("""
            class LinkRenderer {
                init(params) {
                    this.eGui = document.createElement('a');
                    if (params.value) {
                        this.eGui.setAttribute("href", params.value);
                        this.eGui.setAttribute("target", "_blank");
                        this.eGui.innerHTML = params.value;
                    }
                }
                getGui() {
                    return this.eGui;
                }
            }
            """)

            if "URL" in df.columns:
                gb.configure_column("URL", cellRenderer=url_renderer, editable=False, width=250)

            # Set row height and display options
            gb.configure_grid_options(rowHeight=60, rowSelection='none', suppressCopyRowsToClipboard=False, multiSelect=True)
            grid_options = gb.build()

            # Show the grid
            AgGrid(
                df,
                gridOptions=grid_options,
                height=900,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                enable_enterprise_modules=True,
                theme="alpine",
                fit_columns_on_grid_load=True
            )

        except Exception as e:
            st.error(f"Error loading the hidden file: {e}")
    else:
        st.warning("No previous file found.")

elif user_choice == "Upload new file":
    st.subheader("Step 1: Upload your Excel file")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Save the uploaded file as a hidden file with a custom name
        with open(hidden_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())  # Save the file content

        # Load the data
        df = pd.read_excel(
    BytesIO(uploaded_file),        # or uploaded_file for the upload branch
    sheet_name="PIM",
    usecols="A:U",
    header=1,
    dtype={"SKU": str, "URL": str, "Image URL": str}  # <— add this
)

        # Process the dataframe (cleaning and column setup)
        df = process_dataframe(df)
        

 # Your grid configuration logic (highlighting, dropdowns, etc.) remains the same
        yellow_highlight_cols = ["Macro Material_", "Main Color_", "Shape_", "Carry_"]
        df["Complete Status"] = df[yellow_highlight_cols].apply(
            lambda row: 0 if row.isna().any() or any(str(x).strip() == "" for x in row) else 1, axis=1
        ).astype(int)

        # Build grid options
        gb = GridOptionsBuilder.from_dataframe(df)

        # Configure default column behavior
        gb.configure_default_column(
            resizable=True,
            filter=True,
            sortable=True,
            editable=True,
            wrapText=True,
            autoHeight=False,
            cellStyle={"fontSize": "11px", "fontFamily": "Arial, sans-serif", "lineHeight": "1.2"}
        )

        # Add the column configurations for dropdowns, highlights, and custom JS renderers
        yellow_style = JsCode("""
            function(params) {
                if (params.value == null || params.value.toLowerCase() === "blanket") {
                    return { 'backgroundColor': '#ffcc99', 'fontSize': '11px' };
                }
                return { 'backgroundColor': '#fffac8', 'fontSize': '11px' };
            }
        """)

        for col in yellow_highlight_cols:
            if col in df.columns:
                gb.configure_column(col, cellStyle=yellow_style, minWidth=90)

        # Image rendering for URLs
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

        if "Image URL" in df.columns:
            gb.configure_column("Image URL", cellRenderer=image_renderer, editable=False, width=230)

        # Make URLs clickable
        url_renderer = JsCode("""
        class LinkRenderer {
            init(params) {
                this.eGui = document.createElement('a');
                if (params.value) {
                    this.eGui.setAttribute("href", params.value);
                    this.eGui.setAttribute("target", "_blank");
                    this.eGui.innerHTML = params.value;
                }
            }
            getGui() {
                return this.eGui;
            }
        }
        """)

        if "URL" in df.columns:
            gb.configure_column("URL", cellRenderer=url_renderer, editable=False, width=250)


        # Set row height and display options
        gb.configure_grid_options(rowHeight=60, rowSelection='none', suppressCopyRowsToClipboard=False, multiSelect=True)
        grid_options = gb.build()

        # Show the grid
        AgGrid(
            df,
            gridOptions=grid_options,
            height=900,
            allow_unsafe_jscode=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            enable_enterprise_modules=True,
            theme="alpine",
            fit_columns_on_grid_load=True
        )

else:
    st.info("Please upload an Excel file or choose to open the previous file.")

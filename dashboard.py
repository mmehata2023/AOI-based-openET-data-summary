import os

import streamlit as st
import geopandas as gpd
import pandas as pd

import io

from utils.data_utils import load_data

from utils.advanced_figure_utils import (

    annual_timeseries,
    srctype_comparison_plot,
    monthly_boxplot,
    cumulative_plot,
    acres_timeseries
)

from utils.map_utils import (
    create_interactive_map
)

from utils.summary_utils import (
    create_summary_tables
)
from utils.download_utils import (
    create_download_tab
)
from utils.io_utils import (
    read_uploaded_aoi
)



#-----------

st.markdown("""
<style>

/* FORCE header styling */
.dataframe thead th {
    background-color: #2b6cb0 !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    text-align: center !important;
    padding: 10px !important;
    border-bottom: 2px solid #163a5a !important;
}

/* Body cells */
.dataframe tbody td {
    color: #111 !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    text-align: right !important;
    padding: 8px !important;
}


/* Alternating rows */
.dataframe tbody tr:nth-child(even) {
    background-color: #eef2f7 !important;
}

.dataframe tbody tr:nth-child(odd) {
    background-color: #f9f9f9 !important;
}

/* Table border */
.dataframe {
    border: 1px solid #ccc !important;
    border-radius: 6px !important;
}

</style>
""", unsafe_allow_html=True)



# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    layout="wide"
)

# =====================================================
# TAB STYLE
# =====================================================

st.markdown(
    """
    <style>

    /* TAB TEXT */
    button[data-baseweb="tab"] p {

        font-size: 22px !important;

        font-weight: 800 !important;
    }

    /* TAB BUTTON */
    button[data-baseweb="tab"] {

        padding: 10px 28px !important;
    }

    </style>
    """,

    unsafe_allow_html=True
)


# =====================================================
# TITLE
# =====================================================

st.title("AOI-Based StatewideET Summary Dashboard")

st.markdown(
    """
    ### Workflow Instructions
    
    ##### This dashboard visualizes OpenET-derived annual and monthly datasets generated from the AOI extraction workflow.
    
    ------------------------------------------------------------

    #### Directory Structure
    ```text
    app_directory/
    │
    ├── aoi (Oregon Lambert (EPSG: 2992))
    ├── data/(annual& monthly parquet data generated from APP1 (AOI-Based StatewideET Data Extractor)
    ├── utils/
    │   ├── advanced_figure_utils.py
    │   ├── data_utils.py
    │   ├── download_utils.py
    │   ├── io_utils.py
    │   ├── map_utils.py
    │   └── summary_utils.py
    ├── dashboard.py
    └── requirements.txt
    ```
    ------------------------------------------------------------    
    #### Dashboard Workflow (APP2)
    ```text
    Upload AOI ZIP (this is for showing boundary on a Map)
            ↓
    Read Annual GeoParquet (should be inside data folder)
            ↓
    Read Monthly GeoParquet (should be inside data folder)
            ↓
    Interactive Visualization
            ↓
    Filtering, Summarizing, and Downloading Options
    ```

    #### Water Year Definition

    Water Year:
    November (previous year) → October (current year)

    Example:
    WY 1985 = Nov 1984 → Oct 1985

    """
)


# =====================================================
# AOI INPUT
# =====================================================

#uploaded_aoi = st.file_uploader(
#    "Upload AOI ZIP (Just for Map)",
#    type="zip"
#)
st.markdown(
    "<h3 style='color:#ff6600; font-weight:800;'>Upload AOI ZIP (Just for Map)</h3>",
    unsafe_allow_html=True
)

uploaded_aoi = st.file_uploader(
    label="",
    type="zip"
)

#===================================
# HEADING FOR PROJECT
#==================================
if uploaded_aoi is not None:

    project_name = (
        uploaded_aoi.name
        .replace(".zip", "")
        .replace("_aoi", "")
        .replace("_", " ")
        .upper()
    )

    st.markdown(
        f"""
        <h2 style="
            color:#1f4e79;
            font-weight:800;
            margin-top:10px;
            ">
            PROJECT: {project_name}
        </h2>
        """,
        unsafe_allow_html=True
    )
# =====================================================
# READ AOI
# =====================================================

if uploaded_aoi:

    aoi = read_uploaded_aoi(
        uploaded_aoi
    )

else:

    st.warning(
        "Please upload AOI ZIP."
    )

    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

df = load_data()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Filters")

# =====================================================
# VARIABLE DROPDOWN
# =====================================================

VARIABLE_MAP = {

    "ET Reference (in)": "et_reference",

    "ETa (in)": "eta",

    "ETDa (in)": "etda",

    "P_rz (in)": "p_rz",

    "PPT (in)": "ppt",

    "IRR CU (in)": "irr_cu_volumeadj",

    "AW (in)": "aw"
}

selected_label = st.sidebar.selectbox(

    "Variable",

    list(VARIABLE_MAP.keys())
)

selected_var = VARIABLE_MAP[
    selected_label
]

# =====================================================
# WATER YEAR
# =====================================================

water_year = st.sidebar.selectbox(

    "Shifted Water Year (Nov–Oct)",

    sorted(df["wateryear"].unique())
)

# =====================================================
# MONTH ( idon't want this drop down menu)
# =====================================================

#selected_month = st.sidebar.selectbox(

#    "Month",

#    sorted(
#        df["month"]
#        .dropna()
#        .unique()
#    )
#)

# =====================================================
# IRRIGATION FILTER
# =====================================================

irr_option = st.sidebar.selectbox(

    "IRR_STATUS",

    [
        "All fields",
        "Irrigated fields",
        "Non-irrigated fields"
    ]
)

# =====================================================
# SOURCE TYPE FILTER
# =====================================================

src_option = st.sidebar.selectbox(

    "Water Source",

    [
        "All",
        "Rainfed/No-WR",
        "Groundwater",
        "Surfacewater",
        "Mixed"
    ]
)

# =====================================================
# FILTER DATA
# =====================================================

filtered_all = df.copy()

# =====================================================
# IRRIGATION FILTER
# =====================================================

if irr_option == "Irrigated fields":

    filtered_all = filtered_all[

        filtered_all["irr_status"] == 1
    ]

elif irr_option == "Non-irrigated fields":

    filtered_all = filtered_all[

        filtered_all["irr_status"] == 0
    ]

# =====================================================
# SOURCE FILTER
# =====================================================

src_map = {

    "Rainfed/No-WR": 0,

    "Groundwater": 1,

    "Surfacewater": 2,

    "Mixed": 3
}

if src_option != "All":

    filtered_all = filtered_all[

        filtered_all["srctype"] ==

        src_map[src_option]
    ]

# =====================================================
# SINGLE WATER YEAR
# =====================================================

filtered = filtered_all[

    filtered_all["wateryear"] == water_year

].copy()



# =====================================================
# FILTER LABELS
# =====================================================

filter_label = (

    f"IRR_STATUS: {irr_option} | "
    f"Water Source: {src_option}"
)

# =====================================================
# TITLE
# =====================================================

title = (

    f"{selected_label} | "

    f"Shifted Water Year "

    f"(Nov–Oct)"
)




# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(

    [
        "Graphs",
        "Maps",
        "Summary",
        "Downloads"
    ]
)

# =====================================================
# TAB 1 — GRAPHS
# =====================================================

with tab1:

    # =================================================
    # AOI ANNUAL TIMESERIES
    # =================================================

    st.subheader(
        "AOI Annual Mean Time Series |"
        f"{filter_label}"
    )

    fig1 = annual_timeseries(

        filtered_all,

        selected_var,

        f"{selected_label} | "
        f"Shifted Water Year "
        f"(Nov–Oct)"
    )

    st.plotly_chart(
        fig1,
        width="stretch"
    )

    # =================================================
    # SOURCE TYPE COMPARISON
    # =================================================

    st.subheader(
        "Source Type Comparison |"
        f"{filter_label}"
    )

    fig2 = srctype_comparison_plot(

        filtered_all,

        selected_var,

        f"{selected_label} by Source Type | "
        f"Shifted Water Year "
        f"(Nov–Oct)"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

    # =================================================
    # MONTHLY BOXPLOT
    # =================================================


    st.subheader(
        f"Monthly Distribution |"
        f"WY {water_year} |"
        f"{filter_label}"
    )

    fig3 = monthly_boxplot(

        filtered,

        selected_var,

        f"{selected_label} Monthly Distribution | "
        f"WY {water_year} "
        f"(Nov–Oct)"
    )

    st.plotly_chart(
        fig3,
        width="stretch"
    )


    # =================================================
    # CUMULATIVE CURVE
    # =================================================

    st.subheader(
        f"Cumulative Curve |"
        f"WY {water_year} |"
        f"{filter_label}"
    )

    fig4 = cumulative_plot(

        filtered_all,

        selected_var,

        f"{selected_label} Cumulative Curve | "
        f"WY {water_year} "
        f"(Nov–Oct)",
        selected_wy=water_year
    )

    st.plotly_chart(
        fig4,
        width="stretch"
    )



    # =================================================
    # IRRIGATED / NON-IRRIGATED ACRES TIME SERIES
    # =================================================

    st.subheader(
        "Irrigated and Non-Irrigated Acres Time Series"
    )

    fig_acres = acres_timeseries(

        filtered_all,

        "Annual Total Acres | "
        "Shifted WY (Nov–Oct)"
    )

    st.plotly_chart(
        fig_acres,
        width="stretch"
    )

# =====================================================
# TAB 2 — MAPS
# =====================================================

with tab2:

    st.subheader(
        f"Annual Map | "
        f"Shifted WY {water_year} "
        f"(Nov–Oct) |"
        f"{filter_label}"
    )

    # =============================================
    # CREATE ANNUAL FIELD VALUES
    # =============================================

    if selected_var == "et_fraction":

        annual_values = (

            filtered.groupby(
                "openet_id"
            )[selected_var]

            .mean()

            .reset_index()
        )

    else:

        annual_values = (

            filtered.groupby(
                "openet_id"
            )[selected_var]

            .sum()

            .reset_index()
        )

    # =============================================
    # KEEP ONE GEOMETRY PER FIELD
    # =============================================

    geometry_df = (

        filtered[
            [
                "openet_id",
                "geometry"
            ]
        ]

        .drop_duplicates(
            subset="openet_id"
        )
    )


    # =============================================
    # MERGE
    # =============================================

    map_df = annual_values.merge(

        geometry_df,

        on="openet_id",

        how="left"
    )


    # =============================================
    # CONVERT TO GEODATAFRAME
    # =============================================

    map_df = gpd.GeoDataFrame(

        map_df,

        geometry="geometry",
        crs=filtered.crs
    )


    # =============================================
    # CREATE MAP
    # =============================================

    create_interactive_map(

        map_df,

        selected_var,
        aoi=aoi,
        water_year=water_year
    )



# =====================================================
# TAB 3 — SUMMARY
# =====================================================

with tab3:

    #st.subheader(
    #    "Summary Statistics"
    #)


    create_summary_tables(

        df,

        filtered,

        selected_var,

        water_year
    )

# =====================================================
# TAB 4 — DOWNLOADS
# =====================================================
# ============================================
# FILTER ONLY IRRIGATION + SOURCE
# KEEP ALL WATER YEARS
# ============================================

summary_df = df.copy()

# Irrigation filter
if irr_option == "Irrigated fields":
    summary_df = summary_df[
        summary_df["irr_status"] == 1
    ]

elif irr_option == "Non-irrigated fields":
    summary_df = summary_df[
        summary_df["irr_status"] == 0
    ]

# Source filter
if src_option == "Groundwater":
    summary_df = summary_df[
        summary_df["srctype"] == 1
    ]

elif src_option == "Surfacewater":
    summary_df = summary_df[
        summary_df["srctype"] == 2
    ]

elif src_option == "Mixed":
    summary_df = summary_df[
        summary_df["srctype"] == 3
    ]

elif src_option == "Rainfed/No-WR":
    summary_df = summary_df[
        summary_df["srctype"] == 0
    ]


with tab4:

    create_download_tab(
        summary_df,

        filtered,

        selected_var,

        water_year,

        irr_option,

        src_option
    )

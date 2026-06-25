import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# TABLE STYLING
# =====================================================

def style_table(df):
    df = df.copy()

    # Identify numeric columns EXCEPT 'month'
    num_cols = df.select_dtypes(include=[np.number]).columns
    num_cols = [c for c in num_cols if c !="month"]

    # Round numeric columns (except month)
    df[num_cols] = df[num_cols].round(2)

    # Format only numeric columns
    fmt = {col: "{:.2f}" for col in num_cols}

    return (
        df.style
        .format(fmt)
        .set_properties(**{
            "font-size": "16px",
            "font-weight": "600",
            "color": "#111",
            "padding": "8px",
            "text-align": "left" ,  # <— body cell alignment
            "border": "1px solid #DDDDDD"
        })
        .set_table_styles([
            {
                "selector": "th.col_heading",
                "props": [
                    ("background-color", "#3b82c4"),
                    ("color", "white"),
                    ("font-size", "18px"),
                    ("font-weight", "900"),
                    ("text-align", "left"),   # <— header alignment FIX
                    ("padding", "10px")
                ]
            }
        ])
    )


def card_header(title):
    st.markdown(
        f"""
        <div style="
            background-color:#2b6cb0;
            padding:12px 15px;
            border-radius:6px;
            color:white;
            font-size:20px;
            font-weight:800;
            text-align:center;
            margin-top:25px;">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# MAIN SUMMARY FUNCTION
# =====================================================

def create_summary_tables(df, filtered, variable, water_year):

    st.subheader(f"Summary — Shifted Water Year {water_year} (Nov–Oct)")

    df = df.copy()
    filtered = filtered.copy()

    # Convert AC-FT to inches
    if variable in ["irr_cu_volumeadj", "aw"]:
        df[variable] = (df[variable] * 12) / df["acres_ftr_geom"]
        filtered[variable] = (filtered[variable] * 12) / filtered["acres_ftr_geom"]

    # Field-level totals
    if variable == "et_fraction":
        field_totals = (
            filtered.groupby(["openet_id", "irr_status", "acres_ftr_geom"])[variable]
            .mean()
            .reset_index()
        )
    else:
        field_totals = (
            filtered.groupby(["openet_id", "irr_status", "acres_ftr_geom"])[variable]
            .sum()
            .reset_index()
        )

    # Area-weighted mean
    annual_summary = (
        field_totals.groupby("irr_status")
        .apply(lambda x: np.average(x[variable], weights=x["acres_ftr_geom"]))
        .reset_index(name="Annual_WY_Average")
    )

    annual_summary["Irrigation"] = annual_summary["irr_status"].map({
        0: "Non-Irrigated",
        1: "Irrigated"
    })

    annual_summary["Annual_WY_Average"] = annual_summary["Annual_WY_Average"].round(2)

    # Display annual summary
    card_header("Area‑Weighted Annual Water‑Year Average (Nov–Oct)")
    st.table(style_table(annual_summary[["Irrigation", "Annual_WY_Average"]]))

    # Monthly summary
    monthly_summary = (
        filtered.groupby("month")
        .apply(lambda x: np.average(x[variable], weights=x["acres_ftr_geom"]))
        .reset_index(name=variable)
    )

    whole_period = (
        df.groupby("month")
        .apply(lambda x: np.average(x[variable], weights=x["acres_ftr_geom"]))
        .reset_index(name="41yr_avg")
    )

    monthly_summary["41yr_avg"] = whole_period["41yr_avg"]
    monthly_summary = monthly_summary.round(2)

    card_header("Area‑Weighted Monthly Average")
    st.table(style_table(monthly_summary))

    # Acres summary
    unique_fields = (
        filtered[["openet_id", "irr_status","srctype", "acres_ftr_geom"]]
        .drop_duplicates(
            subset = "openet_id"
        )
    )

    acres_summary = (
        unique_fields.groupby(["irr_status", "srctype"])["acres_ftr_geom"]
        .sum()
        .reset_index()
    )

    acres_summary["Irrigation"] = acres_summary["irr_status"].map({
        0: "Non-Irrigated",
        1: "Irrigated"
    })

    acres_summary["Source"] = acres_summary["srctype"].map({
        0: "Rainfed/No-WR",
        1: "Groundwater",
        2: "Surfacewater",
        3: "Mixed"
    })

    acres_summary = acres_summary.rename(columns={"acres_ftr_geom": "Total_Acres"})
    acres_summary["Total_Acres"] = acres_summary["Total_Acres"].round(1)

    card_header("Acres Summary")
    st.table(style_table(acres_summary[["Irrigation", "Source", "Total_Acres"]]))

    # Total acres by irrigation
    irr_total = (
        unique_fields.groupby("irr_status")["acres_ftr_geom"]
        .sum()
        .reset_index()
    )

    irr_total["Irrigation"] = irr_total["irr_status"].map({
        0: "Non-Irrigated",
        1: "Irrigated"
    })

    irr_total = irr_total.rename(columns={"acres_ftr_geom": "Total_Acres"})
    irr_total["Total_Acres"] = irr_total["Total_Acres"].round(1)

    card_header("Total Acres by Irrigation Status")
    st.table(style_table(irr_total[["Irrigation", "Total_Acres"]]))

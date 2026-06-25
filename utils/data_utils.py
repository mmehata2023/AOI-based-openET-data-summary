import os
import glob

import geopandas as gpd
import pandas as pd
import streamlit as st

# ======================================================
# LOAD DATA
# ======================================================

def load_data():

    # ==================================================
    # FIND FILES
    # ==================================================

    annual_files = glob.glob(
        os.path.join(
            "data",
            "*_annual.parquet"
        )
    )

    monthly_files = glob.glob(
        os.path.join(
            "data",
            "*_monthly.parquet"
        )
    )

    # ==================================================
    # CHECK FILES
    # ==================================================

    if len(annual_files) == 0:

        raise FileNotFoundError(
            "No annual parquet found"
        )

    if len(monthly_files) == 0:

        raise FileNotFoundError(
            "No monthly parquet found"
        )

    # ==================================================
    # READ GEOPARQUET
    # ==================================================

    annual = gpd.read_parquet(
        annual_files[0]
    )

    monthly = gpd.read_parquet(
        monthly_files[0]
    )

    # ==================================================
    # STANDARDIZE COLUMN NAMES
    # ==================================================

    annual.columns = [
        c.lower()
        for c in annual.columns
    ]

    monthly.columns = [
        c.lower()
        for c in monthly.columns
    ]

    # ==================================================
    # KEEP IRR STATUS
    # ==================================================

    irr_df = annual[
        [
            "openet_id",
            "year",
            "irr_status"
        ]
    ].copy()



    # ==========================================
    # CREATE WATER YEAR IN MONTHLY
    # ==========================================

    monthly["wateryear"] = monthly["year"]

    monthly.loc[
        monthly["month"] >= 11,
        "wateryear"
    ] += 1

    # ==================================================
    # CREATE WATER YEAR IN ANNUAL
    # ==================================================

    irr_df["wateryear"] = irr_df["year"]

    # ==========================================
    # MERGE USING WATERYEAR
    # ==========================================

    final_df = monthly.merge(

        irr_df[
            [
                "openet_id",
                "wateryear",
                "irr_status"
            ]
        ],

        on=[
            "openet_id",
            "wateryear"
        ],

        how="left"
    )



    # ==================================================
    # CLEAN TYPES
    # ==================================================

    final_df["year"] = (
        final_df["year"]
        .astype(int)
    )

    final_df["month"] = (
        final_df["month"]
        .astype(int)
    )

    final_df["wateryear"] = (
        final_df["wateryear"]
        .astype(int)
    )

    # ==================================================
    # RESTORE GEODATAFRAME
    # ==================================================

    final_df = gpd.GeoDataFrame(
        final_df,
        geometry="geometry",
        crs=monthly.crs
    )


    # ==================================================
    # AREA COLUMN
    # ==================================================

    final_df["area_acres"] = (
        final_df["acres_ftr_geom"]
    )

    # ==================================================
    # CONVERT AC-FT TO INCHES
    # ==================================================

    final_df["aw"] = (

        final_df["aw"] * 12
        / final_df["area_acres"]
    )

    final_df["irr_cu_volumeadj"] = (

        final_df["irr_cu_volumeadj"] * 12
        / final_df["area_acres"]
    )

  
    return final_df

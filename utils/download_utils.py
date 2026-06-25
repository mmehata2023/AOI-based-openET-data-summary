import io
import pandas as pd
import streamlit as st
import numpy as np




# ======================================================
# DOWNLOAD TAB
# ======================================================

def create_download_tab(
    df,
    filtered,
    selected_var,
    water_year,
    irr_option,
    src_option
):

    st.subheader(
        "Download Outputs"
    )

    # ==================================================
    # FILE LABEL
    # ==================================================

    safe_irr = (
        irr_option
        .replace(" ", "_")
        .replace("/", "_")
    )

    safe_src = (
        src_option
        .replace(" ", "_")
        .replace("/", "_")
    )

    base_name = (

        f"{selected_var}_"
        f"WY{water_year}_"
        f"{safe_irr}_"
        f"{safe_src}"
    )


    # ==========================================
    # AOI SUMMARY FILE NAME
    # ==========================================

    aoi_summary_name = f"{selected_var}"

    if irr_option == "Irrigated fields":

        aoi_summary_name += "_irrigated"

    elif irr_option == "Non-irrigated fields":

        aoi_summary_name += "_non_irrigated"

    if src_option != "All":

        aoi_summary_name += (
            "_"
            + src_option.lower()
            .replace("/", "_")
            .replace(" ", "_")
        )

    # ==================================================
    # MONTHLY CSV
    # ==================================================

    monthly_csv = (
        filtered
        .drop(
            columns="geometry",
            errors="ignore"
        )
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(

        label="Download Monthly Field for Selected WY CSV",

        data=monthly_csv,

        file_name=
        f"{base_name}_monthly.csv",

        mime="text/csv"
    )

    # ==================================================
    # ANNUAL SUMMARY
    # ==================================================

    annual = (

        filtered.groupby(
            [
                "openet_id",
                "wateryear"
            ]
        )[selected_var]

        .sum()

        .reset_index()
    )

    annual_csv = (
        annual
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(

        label="Download Annual Field for Selected WY CSV",

        data=annual_csv,

        file_name=
        f"{base_name}_annual.csv",

        mime="text/csv"
    )

    # ==================================================
    # ANNUAL AOI SUMMARY CSV
    # ==================================================

    annual_field = (

        df.groupby(
            [
                "openet_id",
                "wateryear",
                "acres_ftr_geom"
            ]
        )[selected_var]

        .sum()

        .reset_index()
    )

    annual_summary = (

        annual_field.groupby(
            "wateryear"
        )

        .apply(

            lambda x: pd.Series({

                "Acres":
                    x["acres_ftr_geom"].sum(),

                selected_var:
                    np.average(

                        x[selected_var],

                        weights=x["acres_ftr_geom"]
                    )
            })
        )

        .reset_index()
    )


    annual_summary["Acres"] = (
        annual_summary["Acres"]
        .round(1)
    )

    annual_summary[selected_var] = (
        annual_summary[selected_var]
        .round(2)
    )

    annual_summary_csv = (
        annual_summary
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(

        label="Download Annual AOI Summary for All WYs CSV",

        data=annual_summary_csv,

        file_name=
        f"{aoi_summary_name}_annual_aoi_summary_all_wy.csv",

        mime="text/csv"
    )

    # ==================================================
    # MONTHLY AOI SUMMARY CSV
    # ==================================================

    monthly_summary = (

        df.groupby(
            [
                "wateryear",
                "month"
            ]
        )

        .apply(

            lambda x: pd.Series({

                "Acres":
                    x.drop_duplicates("openet_id")[
                        "acres_ftr_geom"
                    ].sum(),

                selected_var:
                    np.average(

                        x[selected_var],

                        weights=x["acres_ftr_geom"]
                    )
            })
        )

        .reset_index()
    )


    monthly_summary["Acres"] = (
        monthly_summary["Acres"]
        .round(1)
    )

    monthly_summary[selected_var] = (
        monthly_summary[selected_var]
        .round(2)
    )

    monthly_summary_csv = (
        monthly_summary
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(

        label="Download Monthly AOI Summary for All WYs CSV",

        data=monthly_summary_csv,

        file_name=
        f"{aoi_summary_name}_monthly_aoi_summary_all_wy.csv",

        mime="text/csv"
    )


    
    # ==================================================
    # GEOPARQUET
    # ==================================================

    parquet_buffer = io.BytesIO()

    filtered.to_parquet(
        parquet_buffer,
        index=False
    )

    parquet_buffer.seek(0)

    st.download_button(

        label="Download GeoParquet",

        data=parquet_buffer,

        file_name=
        f"{base_name}.parquet",

        mime="application/octet-stream"
    )

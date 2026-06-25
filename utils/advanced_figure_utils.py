import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots


# =========================================================
# STANDARD LAYOUT
# =========================================================

def apply_standard_layout(
    fig,
    title
):

    fig.update_layout(

        template="simple_white",

        title=dict(
            text=title,
            x=0.5,
            xanchor="center",

            font=dict(
                size=24,
                color="black",
                family="Arial Black"
            )
        ),

        font=dict(
            family="Arial",
            size=16,
            color="black"
        ),

        width=1200,
        height=650,

        margin=dict(
            l=50,
            r=50,
            t=90,
            b=50
        ),

        plot_bgcolor="white",

        paper_bgcolor="white",

        legend=dict(

            orientation="h",

            yanchor="bottom",
            y=1.02,

            xanchor="right",
            x=1,

            font=dict(
                size=15,
                color="black"
            )
        )
    )

    # =====================================================
    # X AXIS
    # =====================================================

    fig.update_xaxes(

        showgrid=True,

        gridwidth=1,

        gridcolor="lightgray",

        showline=True,

        linewidth=2,

        linecolor="black",

        mirror=True,

        title_font=dict(
            size=20,
            color="black",
            family="Arial Black"
        ),

        tickfont=dict(
            size=15,
            color="black"
        )
    )

    # =====================================================
    # Y AXIS
    # =====================================================

    fig.update_yaxes(

        showgrid=True,

        gridwidth=1,

        gridcolor="lightgray",

        showline=True,

        linewidth=2,

        linecolor="black",

        mirror=True,

        title_font=dict(
            size=20,
            color="black",
            family="Arial Black"
        ),

        tickfont=dict(
            size=15,
            color="black"
        )
    )

    return fig


# =========================================================
# 1. AOI ANNUAL TIMESERIES
# =========================================================

def annual_timeseries(
    df,
    variable,
    title
):

    # =====================================================
    # FIELD WATER-YEAR VALUES
    # =====================================================

    if variable == "et_fraction":

        field_annual = (

            df.groupby(
                [
                    "openet_id",
                    "wateryear",
                    "area_acres"
                ]
            )[variable]

            .mean()
            .reset_index()
        )

    else:

        field_annual = (

            df.groupby(
                [
                    "openet_id",
                    "wateryear",
                    "area_acres"
                ]
            )[variable]

            .sum()
            .reset_index()
        )

    # =====================================================
    # AREA-WEIGHTED AOI MEAN
    # =====================================================

    annual_df = (

        field_annual.groupby(
            "wateryear"
        )

        .apply(

            lambda x: np.average(

                x[variable],

                weights=x["area_acres"]
            )
        )

        .reset_index(name=variable)
    )

    # =====================================================
    # PLOT
    # =====================================================

    fig = px.line(

        annual_df,

        x="wateryear",
        y=variable,

        markers=True
    )

    fig.update_traces(
        line=dict(width=4)
    )

    fig.update_layout(

        xaxis_title="Shifted Water Year (Nov–Oct)",

        yaxis_title=f"{variable} Annual Mean",

        hovermode="x unified"
    )

    fig = apply_standard_layout(
        fig,
        title
    )

    return fig


# =========================================================
# 2. SOURCE TYPE COMPARISON
# =========================================================

def srctype_comparison_plot(
    df,
    variable,
    title
):

    # =====================================================
    # FIELD WATER-YEAR VALUES
    # =====================================================

    if variable == "et_fraction":

        field_annual = (

            df.groupby(
                [
                    "openet_id",
                    "wateryear",
                    "srctype",
                    "area_acres"
                ]
            )[variable]

            .mean()
            .reset_index()
        )

    else:

        field_annual = (

            df.groupby(
                [
                    "openet_id",
                    "wateryear",
                    "srctype",
                    "area_acres"
                ]
            )[variable]

            .sum()
            .reset_index()
        )

    # =====================================================
    # AREA-WEIGHTED MEAN BY SOURCE TYPE
    # =====================================================

    src = (

        field_annual.groupby(
            [
                "wateryear",
                "srctype"
            ]
        )

        .apply(

            lambda x: np.average(

                x[variable],

                weights=x["area_acres"]
            )
        )

        .reset_index(name=variable)
    )

    # =====================================================
    # LABELS
    # =====================================================

    src["srctype"] = (

        src["srctype"]

        .map({
            0: "Rainfed/No-WR",
            1: "Groundwater",
            2: "Surfacewater",
            3: "Mixed"
        })
    )

    # =====================================================
    # PLOT
    # =====================================================

    fig = px.line(

        src,

        x="wateryear",
        y=variable,

        color="srctype",

        markers=True,

        color_discrete_map={

            "Rainfed/No-WR": "gray",

            "Groundwater": "blue",

            "Surfacewater": "orange",

            "Mixed": "green"
        }
    )

    fig.update_traces(
        line=dict(width=3)
    )

    fig.update_layout(

        xaxis_title="Shifted Water Year (Nov–Oct)",

        yaxis_title=f"{variable} Annual Mean",

        legend_title="Source Type",

        hovermode="x unified"
    )

    fig = apply_standard_layout(
        fig,
        title
    )

    return fig


# =========================================================
# 3. MONTHLY BOXPLOT
# =========================================================

def monthly_boxplot(
    df,
    variable,
    title
):

    # =====================================================
    # COPY
    # =====================================================

    df = df.copy()

    # =====================================================
    # WATER YEAR MONTH LABELS
    # =====================================================

    month_map = {

        11: "Nov",
        12: "Dec",
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct"
    }

    df["month_label"] = (
        df["month"]
        .map(month_map)
    )

    # =====================================================
    # FIGURE
    # =====================================================

    fig = px.box(

        df,

        x="month_label",

        y=variable,

        points=False,

        category_orders={

            "month_label": [

                "Nov",
                "Dec",
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct"
            ]
        }
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        xaxis_title="Water Year Month",

        yaxis_title=variable
    )

    # =====================================================
    # AXIS STYLE
    # =====================================================

    fig.update_xaxes(

        title_font=dict(size=20),

        tickfont=dict(size=16)
    )

    fig.update_yaxes(

        title_font=dict(size=20),

        tickfont=dict(size=16)
    )

    fig = apply_standard_layout(
        fig,
        title
    )

    return fig

# =========================================================
# 4. CUMULATIVE CURVE
# =========================================================

def cumulative_plot(
    df,
    variable,
    title,
    selected_wy
):

    # =====================================================
    # AREA-WEIGHTED MONTHLY MEAN
    # =====================================================

    monthly = (

        df.groupby(
            [
                "wateryear",
                "month"
            ]
        )

        .apply(

            lambda x: np.average(

                x[variable],

                weights=x["area_acres"]
            )
        )

        .reset_index(name=variable)
    )

    # =====================================================
    # CREATE WATER YEAR ORDER
    # =====================================================

    monthly["wy_month_order"] = monthly["month"].replace({

        11: 1,
        12: 2,
        1: 3,
        2: 4,
        3: 5,
        4: 6,
        5: 7,
        6: 8,
        7: 9,
        8: 10,
        9: 11,
        10: 12
    })

    # =====================================================
    # MONTH LABELS
    # =====================================================

    month_map = {

        1: "Nov",
        2: "Dec",
        3: "Jan",
        4: "Feb",
        5: "Mar",
        6: "Apr",
        7: "May",
        8: "Jun",
        9: "Jul",
        10: "Aug",
        11: "Sep",
        12: "Oct"
    }

    monthly["wy_month_label"] = (

        monthly["wy_month_order"]
        .map(month_map)
    )

    # =====================================================
    # SORT
    # =====================================================

    monthly = monthly.sort_values(
        [
            "wateryear",
            "wy_month_order"
        ]
    )

    # =====================================================
    # CUMULATIVE
    # =====================================================

    monthly["Cumulative"] = (

        monthly.groupby(
            "wateryear"
        )[variable]

        .cumsum()
    )

    # =====================================================
    # SELECTED WATER YEAR
    # =====================================================

    selected_df = monthly[
        monthly["wateryear"] == selected_wy
    ].copy()

    # =====================================================
    # 41-YEAR CLIMATOLOGY
    # =====================================================

    climatology = (

        monthly.groupby(
            [
                "wy_month_order",
                "wy_month_label"
            ]
        )[variable]

        .mean()
        .reset_index()
    )

    climatology = climatology.sort_values(
        "wy_month_order"
    )

    # =====================================================
    # 41-YEAR CUMULATIVE
    # =====================================================

    climatology["Cumulative_41yr"] = (

        climatology[variable]
        .cumsum()
    )

    # =====================================================
    # FIGURE
    # =====================================================

    fig = go.Figure()

    # -----------------------------------------------------
    # SELECTED WY
    # -----------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=selected_df["wy_month_label"],

            y=selected_df["Cumulative"],

            mode="lines+markers",

            name=f"WY {selected_wy}",

            line=dict(
                width=5,
                color="blue"
            )
        )
    )

    # -----------------------------------------------------
    # 41-YEAR AVERAGE
    # -----------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=climatology["wy_month_label"],

            y=climatology["Cumulative_41yr"],

            mode="lines+markers",

            name="41-Year Average",

            line=dict(
                width=5,
                color="black",
                dash="dash"
            )
        )
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        xaxis_title="Water Year Month",

        yaxis_title=f"Cumulative {variable}",

        hovermode="x unified"
    )

    fig = apply_standard_layout(
        fig,
        title
    )

    return fig


# =========================================================
# 5. ACRES TIME SERIES
# =========================================================

def acres_timeseries(
    df,
    title
):

    # =====================================================
    # UNIQUE FIELD ACRES BY WATER YEAR + IRRIGATION STATUS
    # =====================================================

    acres_df = (

        df[
            [
                "openet_id",
                "wateryear",
                "irr_status",
                "acres_ftr_geom"
            ]
        ]

        .drop_duplicates(
            subset=[
                "openet_id",
                "wateryear"
            ]
        )
    )

    acres_summary = (

        acres_df.groupby(
            [
                "wateryear",
                "irr_status"
            ]
        )["acres_ftr_geom"]

        .sum()

        .reset_index()
    )

    acres_summary["Irrigation"] = (

        acres_summary["irr_status"]

        .map({
            0: "Non-Irrigated",
            1: "Irrigated"
        })
    )

    fig = px.line(

        acres_summary,

        x="wateryear",

        y="acres_ftr_geom",

        color="Irrigation",

        markers=True
    )

    fig.update_traces(
        line=dict(width=4)
    )

    fig.update_layout(

        xaxis_title="Shifted Water Year (Nov–Oct)",

        yaxis_title="Acres",

        legend_title="Irrigation Status",

        hovermode="x unified"
    )

    fig = apply_standard_layout(
        fig,
        title
    )

    return fig

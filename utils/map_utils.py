import json
import geopandas as gpd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import numpy as np
import streamlit as st


# =====================================================
# CLEAN JSON TYPES
# =====================================================

def clean_json_columns(gdf):

    for col in gdf.columns:

        if str(gdf[col].dtype).startswith(
            "datetime"
        ):

            gdf[col] = (
                gdf[col]
                .astype(str)
            )

    return gdf



def create_interactive_map(
    gdf,
    variable,
    aoi=None,
    water_year=None
):

    # =============================================
    # EMPTY
    # =============================================

    if gdf is None or len(gdf) == 0:
        return

    # =============================================
    # FORCE GEODATAFRAME
    # =============================================

    gdf = gpd.GeoDataFrame(
        gdf,
        geometry="geometry"
    )

    # =============================================
    # REMOVE BAD GEOMETRIES
    # =============================================

    gdf = gdf[
        gdf.geometry.notnull()
    ]

    gdf = gdf[
        gdf.geometry.is_valid
    ]

    # =============================================
    # KEEP COLUMNS
    # =============================================

    gdf = gdf[
        [
            "openet_id",
            variable,
            "geometry"
        ]
    ].copy()

    
    

    # =============================================
    # FIX INCORRECT CRS FROM PARQUET
    # =============================================

    gdf = gdf.set_crs(
        "EPSG:2992",
        allow_override=True
        )

    gdf = gdf.to_crs(
        "EPSG:4326"
        )


    # Optional light simplification
    gdf["geometry"] = (
        gdf.geometry.simplify(
            0.0003,
            preserve_topology=True
        )
    )

    # =============================================
    # AOI CRS
    # =============================================

    if aoi is not None:

        if aoi.crs is None:

            aoi = aoi.set_crs(
                "EPSG:5070"
            )

        aoi = aoi.to_crs(
            "EPSG:4326"
        )

    aoi = clean_json_columns(
        aoi
    )

    # =============================================
    # COLOR MAP
    # =============================================

    vmin = gdf[variable].min()
    vmax = gdf[variable].max()

    colormap = cm.linear.YlGnBu_09.scale(
        vmin,
        vmax
    )

    colormap.caption = variable.upper()



    # =============================================
    # CREATE MAP
    # =============================================

    m = folium.Map(

        location=[45.5, -120.5],

        zoom_start=8,

        control_scale=True,

        tiles=None,

        prefer_canvas=True,
        zoom_snap =0.25, ## allow quarter-step zoom levels
        zoom_delta = 0.25 # zoom buttons change by 0.25
    )
    # Title on the map
    #translateX(-50%)
    title_html = f"""
    <div style="
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background-color: white;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid #2b6cb0;
        font-size: 15px;
        font-weight: 700;
        color: #1f4e79;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.2);
    ">
    Annual Map | WY {water_year} | {variable.upper()}
    </div>
    """
    # add title here
    m.get_root().html.add_child(folium.Element(title_html))


    
    # =============================================
    # BASEMAPS
    # =============================================

    # OpenStreetMap
    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap"
    ).add_to(m)

    # Light basemap
    folium.TileLayer(
        "CartoDB positron",
        name="CartoDB Positron"
    ).add_to(m)

    # Dark basemap
    folium.TileLayer(
        "CartoDB dark_matter",
        name="Dark Map"
    ).add_to(m)

    # Terrain
    folium.TileLayer(
        tiles="Stamen Terrain",
        name="Terrain",
        attr="Stamen"
    ).add_to(m)


    # ESRI Hybrid
    folium.TileLayer(
        tiles=
        "https://services.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}",

        attr="Esri",

        name="Hybrid Imagery",

        overlay=False,

        control=True
    ).add_to(m)



    # =============================================
    # TOOLTIP
    # =============================================

    tooltip = folium.GeoJsonTooltip(

        fields=[
            "openet_id",
            variable
        ],

        aliases=[
            "OPENET_ID",
            variable.upper()
        ],

        localize=True
    )

    # =============================================
    # GEOJSON
    # =============================================

    geojson_data = json.loads(
        gdf.to_json()
    )

    # =============================================
    # AOI BOUNDARY
    # =============================================

    if aoi is not None:

        folium.GeoJson(

            aoi,

            name="AOI Boundary",

            style_function=lambda x: {

                "fillColor": "#00000000",

                "color": "red",

                "weight": 3,

                "dashArray": "5,5"
            }

        ).add_to(m)


 

    # =============================================
    # FIELD LAYER
    # =============================================

    
    folium.GeoJson(

        geojson_data,

        name="Fields",

        tooltip=tooltip,

        style_function=lambda feature: {

        "fillColor": colormap(
            feature["properties"][variable]
        ),

        "color": "black",

        "weight": 0.3,

        "fillOpacity": 0.7
        }
    ).add_to(m)

    # =============================================
    # ADD LEGEND
    # =============================================

    colormap.add_to(m)
   

    # =============================================
    # LAYER CONTROL
    # VERY IMPORTANT: ADD AT END
    # =============================================

    folium.LayerControl(
        collapsed=False
    ).add_to(m)

    # =============================================
    # FIT TO AOI
    # =============================================

    # if aoi is not None:

    #     aoi_bounds = aoi.total_bounds

    #     m.fit_bounds([

    #         [aoi_bounds[1], aoi_bounds[0]],

    #         [aoi_bounds[3], aoi_bounds[2]]
    #     ])
    
    
    
    # =============================================
    # FIT TO FIELD BOUNDS
    # =============================================

    field_bounds = gdf.total_bounds

    m.fit_bounds([

        [field_bounds[1], field_bounds[0]],

        [field_bounds[3], field_bounds[2]]
        ])
    # =============================================
    # DISPLAY
    # =============================================
    st_folium(

        m,

        width=1200,

        height=700,

        returned_objects=[]
    )



    # =============================================
    # CREATE A FRESH MAP FOR EXPORT
    # =============================================
    export_map = folium.Map(
        location=m.location,
        zoom_start=m.options.get("zoomStart", 8),
        control_scale=True,
        tiles=None
    )

    # Copy layers from original map
    for child in m._children.values():
        export_map.add_child(child)

    # Add legend ONLY to export map
    colormap.add_to(export_map)

    #==========================================
    # Download html option

    html_map = m.get_root().render()

    st.download_button(
        label="📥 Download HTML Interactive Map",
        data=html_map,
        file_name=f"{variable}_WY{water_year}_map.html",
        mime="text/html"
    )

    

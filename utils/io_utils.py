import os
import zipfile
import tempfile
import geopandas as gpd


# =====================================================
# READ UPLOADED AOI
# =====================================================

def read_uploaded_aoi(uploaded_zip):

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(
        uploaded_zip,
        "r"
    ) as zip_ref:

        zip_ref.extractall(temp_dir)

    shp_files = [

        f for f in os.listdir(temp_dir)

        if f.endswith(".shp")
    ]

    shp_path = os.path.join(
        temp_dir,
        shp_files[0]
    )

    aoi = gpd.read_file(
        shp_path
    )

    return aoi

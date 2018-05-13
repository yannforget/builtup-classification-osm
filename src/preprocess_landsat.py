"""Pre-process Landsat scenes. The scenes are already processed to
surface reflectance values using the Landsat Surface Reflectance Code (LaSRC)
available on github: https://github.com/USGS-EROS/espa-surface-reflectance .

The following script masks the input scenes according to the automatically
generated 40km x 40km areas of interest.
"""

import json
import os

import rasterio
import rasterio.mask
from tqdm import tqdm

from config import CITIES, DATA_DIR
from metadata import City

# Landsat 8 bands filenames after pre-processing
# with Landsat Source Reflectance Code (LaSRC)
BANDS = {
    'blue': '{pid}_sr_band2.tif',
    'green': '{pid}_sr_band3.tif',
    'red': '{pid}_sr_band4.tif',
    'nir': '{pid}_sr_band5.tif',
    'swir1': '{pid}_sr_band6.tif',
    'swir2': '{pid}_sr_band7.tif',
    'tir1': '{pid}_bt_band10.tif',
    'tir2': '{pid}_bt_band11.tif',
    'cfmask': '{pid}_cfmask.tif'
}


def mask_scene(src_dir, dst_dir, product_id, aoi):
    """Mask a Landsat scene given its product identifier and an
    area of interest.
    """
    os.makedirs(dst_dir, exist_ok=True)
    for band, filename in BANDS.items():
        filename = filename.format(pid=product_id)
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, '{}.tif'.format(band))
        mask_band(src_path, dst_path, aoi)


def mask_band(src_path, dst_path, aoi):
    """Mask input band according to the provided GeoJSON-like AOI."""
    masking_shapes = [aoi['geometry']]

    with rasterio.open(src_path) as src:

        dst_profile = src.profile.copy()
        img, dst_affine = rasterio.mask.mask(
            src, masking_shapes, crop=True, all_touched=True)
        img = img[0, :, :]

        # Update rasterio profile with new affine & shape
        dst_profile.update(
            height=img.shape[0],
            width=img.shape[1],
            affine=dst_affine,
            transform=None
        )

        with rasterio.open(dst_path, 'w', **dst_profile) as dst:
            dst.write(img, 1)


if __name__ == '__main__':
    progress = tqdm(total=len(CITIES))
    for city_name in CITIES:
        city = City(city_name)
        aoi_path = os.path.join(city.intermediary_dir, 'masks', 'aoi.geojson')
        with open(aoi_path) as f:
            aoi = json.load(f)
        mask_scene(
            src_dir=os.path.join(DATA_DIR, 'input', 'landsat', city.product_id),
            dst_dir=city.landsat_dir,
            product_id=city.product_id,
            aoi=aoi
        )
        progress.update(1)
    progress.close()

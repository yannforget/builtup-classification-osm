"""Pre-processing of reference polygons."""

import os

import numpy as np
import rasterio
from tqdm import tqdm

from metadata import CITIES, City
from raster import rasterize

if __name__ == '__main__':

    progress = tqdm(total=len(CITIES) * 4)

    for city_name in CITIES:

        city = City(city_name)

        output_dir = os.path.join(city.intermediary_dir, 'reference')
        os.makedirs(output_dir, exist_ok=True)

        shape = (city.profile['height'], city.profile['width'])
        reference = np.zeros(shape=shape, dtype=np.uint8)

        labels = ['builtup', 'baresoil', 'lowveg', 'highveg']
        shapefiles = [
            city.reference_builtup,
            city.reference_baresoil,
            city.reference_lowveg,
            city.reference_highveg
        ]

        for i, (label, shapefile) in enumerate(zip(labels, shapefiles)):

            land_cover = rasterize(shapefile, city.profile).astype(np.bool)
            reference[land_cover] = i + 1
            progress.update(1)

        output_f = os.path.join(output_dir, 'reference.tif')
        profile = city.profile.copy()
        profile.update(dtype=reference.dtype.name, nodata=None)
        with rasterio.open(output_f, 'w', **profile) as dst:
            dst.write(reference, 1)

        progress.update(1)

    progress.close()

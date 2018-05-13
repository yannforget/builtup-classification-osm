"""Generate tiles for several rasters (training data, test data, results)
for visualization in Leaflet:

    1. Colorize the raster according to a custom colormap.
    2. Reproject it to EPSG:4326.
    3. Convert it to RGB Byte.
    4. Generate tiles with GDAL.

Usage:
    python process.py <city>
"""

import os
import sys
import json
import rasterio
import numpy as np
import subprocess


RED = [227, 26, 28]
LIGHT_GREEN = [178, 223, 138]
DARK_GREEN = [51, 160, 44]
ORANGE = [255, 127, 0]


def transform_colors(img, colormap):
    """Transform input raster values to given RGB colors."""
    rgb = np.zeros(shape=(3, img.shape[0], img.shape[1]))
    for value, color in colormap.items():
        for channel in (0, 1, 2):
            rgb[channel, img == value] = color[channel]
    return rgb


def write_rgb(img, dst_profile, dst_path):
    """Write raster to disk with Rasterio."""
    profile = dst_profile.copy()
    profile.update(count=3, dtype=img.dtype.name, nodata=0)
    with rasterio.open(dst_path, 'w', **profile) as dst:
        for channel in (0, 1, 2):
            dst.write(img[channel, :], channel+1)
    return


def reproject_raster(src_path, dst_path, src_epsg):
    """Reproject raster to EPSG:4326 with gdalwarp."""
    subprocess.run([
        'gdalwarp', src_path, dst_path,
        '-s_srs', 'EPSG:{}'.format(src_epsg),
        '-t_srs', 'EPSG:4326'
    ])
    return


def generate_tiles(src_path, dst_dir):
    """Generate XYZ tiles with gdal2tiles."""
    tmp_path = src_path.replace('.tif', '_byte.tif')
    subprocess.run([
        'gdal_translate', '-ot', 'Byte',
        src_path, tmp_path
    ])
    subprocess.run([
        'gdal2tiles_parallel.py', '-p', 'mercator', '-r', 'near',
        '-z', '1-15', '-a', '0,0,0', '--format=PNG',
        tmp_path, dst_dir
    ])
    os.remove(tmp_path)
    return


def write_bounds(raster_path, output_dir):
    """Write bounds coordinates to a JSON file."""
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
    coordinates = {
        'lon_min': bounds.left,
        'lat_min': bounds.bottom,
        'lon_max': bounds.right,
        'lat_max': bounds.top
    }
    with open(os.path.join(output_dir, 'bounds.json'), 'w') as f:
        json.dump(coordinates, f)
    return


def main(data_dir, output_dir, city):
    """Reproject, colorize and tile input rasters."""
    # raster paths
    test_f = os.path.join(
        data_dir, 'intermediary', city, 'reference', 'reference.tif')
    train_f = os.path.join(
        data_dir, 'output', city, 'osm_b', 'training_dataset.tif')
    result_f = os.path.join(
        data_dir, 'output', city, 'osm_b', 'map.tif')

    # colormaps
    cmap_test = {1: RED, 2: ORANGE, 3: LIGHT_GREEN, 4: DARK_GREEN}
    cmap_train = {1: RED, 2: DARK_GREEN}
    cmap_result = {1: RED}

    paths = [test_f, train_f, result_f]
    cmaps = [cmap_test, cmap_train, cmap_result]
    labels = ['test', 'train', 'result']

    for path, cmap, label in zip(paths, cmaps, labels):

        with rasterio.open(path) as src:
            img = src.read(1)
            src_profile = src.profile
            src_epsg = src.crs['init'].split(':')[-1]

        # Colorize raster
        rgb = transform_colors(img, cmap)
        rgb_f = os.path.join(output_dir, '{}_rgb.tif'.format(label))
        write_rgb(rgb, src_profile, rgb_f)

        # Reproject to Mercator
        reproj_f = os.path.join(output_dir, '{}_reproj.tif'.format(label))
        reproject_raster(rgb_f, reproj_f, src_epsg)

        # Generate tiles
        dst_dir = os.path.join(output_dir, '{}_tiles'.format(label))
        generate_tiles(reproj_f, dst_dir)

    write_bounds(os.path.join(output_dir, 'result_reproj.tif'), output_dir)

    for f in os.listdir(output_dir):
        if f.endswith('.tif'):
            os.remove(os.path.join(output_dir, f))


if __name__ == '__main__':

    city = sys.argv[1]
    data_dir = '/home/yann/Work/MAUPP/Code/Landsat_OpenStreetMap/data'
    report_dir = '/home/yann/Work/MAUPP/Code/Landsat_OpenStreetMap/reports/'
    output_dir = os.path.join(report_dir, 'data', city)
    os.makedirs(output_dir, exist_ok=True)
    main(data_dir, output_dir, city)

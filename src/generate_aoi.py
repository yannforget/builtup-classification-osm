"""Generate area of interests for each case study."""

import json
import os
from functools import partial

import pyproj
from shapely.geometry import Point, mapping
from shapely.ops import transform
from tqdm import tqdm

from metadata import City, CITIES


def reproject_geom(geom, src_epsg, dst_epsg):
    """Reproject a shapely geometry given a source EPSG and a
    target EPSG.
    """
    src_proj = pyproj.Proj(init='epsg:{}'.format(src_epsg))
    dst_proj = pyproj.Proj(init='epsg:{}'.format(dst_epsg))
    reproj = partial(pyproj.transform, src_proj, dst_proj)
    return transform(reproj, geom)


def buffer_extent(lat, lon, dst_epsg, buffer_size):
    """Generate a buffer around a location and returns
    the geometry corresponding to its spatial envelope.
    """
    center = reproject_geom(
        Point(lon, lat), src_epsg=4326, dst_epsg=dst_epsg)
    buffer = center.buffer(buffer_size)
    return buffer.exterior.envelope


def geojson_crs(epsg):
    """Generate a GeoJSON CRS member from an EPSG code."""
    epsg = int(epsg)
    if epsg == 4326:
        coordinate_order = [1, 0]
    else:
        coordinate_order = [0, 1]
    return {
        'type': 'EPSG',
        'properties': {'code': epsg, 'coordinate_order': coordinate_order}}


def as_geojson(geom, epsg=None):
    """Get a GeoJSON-like dictionnary of a single shapely geometry."""
    geojson = {'type': 'Feature', 'geometry': mapping(geom)}
    if epsg:
        geojson.update(crs=geojson_crs(epsg))
    return geojson


def write(geom, output_f):
    """Write a GeoJSON-like dictionnary to disk."""
    geojson = json.dumps(geom, indent=True)
    os.makedirs(os.path.dirname(output_f), exist_ok=True)
    with open(output_f, 'w') as f:
        f.write(geojson)
    return


if __name__ == '__main__':
    progress = tqdm(total=len(CITIES))
    for city_name in CITIES:
        city = City(city_name)
        lat, lon = city.location
        extent = buffer_extent(lat, lon, city.epsg, buffer_size=20000)
        extent = as_geojson(extent, city.epsg)
        output_f = os.path.join(city.intermediary_dir, 'masks', 'aoi.geojson')
        write(extent, output_f)
        progress.update(1)
    progress.close()

"""Download OpenStreetMap data for each case study according to their
area of interest using the Overpass API, and pre-process input data
to shapefiles or GeoTIFF.
"""

import os

import geopandas as gpd
import overpass
from shapely.geometry import Polygon, shape
from tqdm import tqdm

from generate_aoi import reproject_geom
from metadata import City, CITIES

OSM_FEATURES = {
    'highway': 'roads.shp',
    'building': 'buildings.shp',
    'leisure': 'leisure.shp',
    'natural': 'natural.shp',
    'landuse': 'landuse.shp'
}


def ways_to_polygons(ways):
    """Polygon geometry type doesn't exist in the OSM database.
    This function convert the closed `ways` geometries of a given
    GeoDataFrame to the polygon geometry type.
    """
    # Only valid geometries
    ways = ways[ways.is_valid]
    # Only geometries with at least 3 nodes
    ways = ways[ways.geometry.map(
        lambda x: len(x.coords) >= 4
    )]
    ways.geometry = ways.geometry.map(
        lambda x: Polygon(x)
    )
    return ways


class Downloader():
    """OpenStreetMap data downloader."""

    def __init__(self, aoi, epsg, dst_dir):
        """Initialize an instance of the overpass API
        for a given case study.
        """
        self.aoi = aoi
        self.epsg = epsg
        self.dst_dir = dst_dir
        self.api = overpass.API()
        self.bbox = self.get_bbox()

    def get_bbox(self):
        """Get bounding box as a formatted string, as expected
        by the overpass API.
        """
        aoi = reproject_geom(
            self.aoi, src_epsg=self.epsg, dst_epsg=4326)
        xmin, ymin, xmax, ymax = [round(coord, 3) for coord in aoi.bounds]
        bbox = '({ymin},{xmin},{ymax},{xmax})'
        return bbox.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)

    def get_feature(self, key):
        """Get all OSM features which have a non-null value for
        a given key. Overpass response is returned as a GeoDataFrame.
        """
        query = overpass.WayQuery('[{}]{}'.format(key, self.bbox))
        response = self.api.Get(query)
        features = gpd.GeoDataFrame.from_features(response)
        features.crs = {'init': 'epsg:4326'}
        features = features[['geometry', key]]
        features = features[features.is_valid]
        features = features[features.geometry.type == 'LineString']

        # Convert ways to polygons except for roads
        if key != 'highway':
            features = ways_to_polygons(features)

        return features


if __name__ == '__main__':

    progress = tqdm(total=len(CITIES) * len(OSM_FEATURES))

    for city_name in CITIES:

        city = City(city_name)
        dst_dir = os.path.join(city.intermediary_dir, 'osm')
        os.makedirs(dst_dir, exist_ok=True)

        osm = Downloader(
            aoi=shape(city.aoi),
            epsg=city.epsg,
            dst_dir=dst_dir
        )

        for key, filename in OSM_FEATURES.items():

            features = osm.get_feature(key)
            features = features[features.is_valid]
            features = features.to_crs(city.crs)
            features = features[features.intersects(shape(city.aoi))]
            geoms = features.intersection(shape(city.aoi))
            features = features.assign(geometry=geoms)
            output_f = os.path.join(dst_dir, filename)
            features.to_file(output_f)
            progress.update(1)

    progress.close()

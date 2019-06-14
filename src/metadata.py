"""City-level metadata."""

import os
import json

import pandas as pd
import geopandas as gpd
import rasterio

# Main directories
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(MODULE_DIR, '..'))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')

# Cities to process
CITIES = [
    'antananarivo',
    'chimoio',
    'dakar',
    'gao',
    'johannesburg',
    'kampala',
    'katsina',
    'nairobi',
    'saint_louis',
    'windhoek'
]


class City(object):
    """Access city-level metadata."""

    def __init__(self, city_name):
        self.data_dir = DATA_DIR
        self.name = city_name
        self.metadata = self.read()

    def read(self):
        """Read CSV metadata file."""
        csv_f = os.path.join(self.data_dir, 'input', 'metadata.csv')
        return pd.read_csv(csv_f, index_col=0)

    @property
    def input_dir(self):
        """Where input raw data files are stored."""
        return os.path.join(self.data_dir, 'input')

    @property
    def intermediary_dir(self):
        """Where intermediary data files are stored."""
        return os.path.join(self.data_dir, 'intermediary', self.name)

    @property
    def output_dir(self):
        """Where output files are saved."""
        return os.path.join(self.data_dir, 'output', self.name)

    @property
    def landsat_dir(self):
        """Where pre-processed Landsat data are stored."""
        return os.path.join(self.intermediary_dir, 'landsat')

    @property
    def reference_dir(self):
        """Where reference data are stored."""
        return os.path.join(self.input_dir, 'reference', self.name)

    @property
    def cache_dir(self):
        """Where cache data is stored."""
        return os.path.join(self.intermediary_dir, 'cache')

    @property
    def epsg(self):
        """Get EPSG code."""
        return self.metadata.at[(self.name, 'epsg')]

    @property
    def crs(self):
        """CRS as a dictionnary."""
        return {'init': 'epsg:{}'.format(self.epsg)}

    @property
    def location(self):
        """Latitude & longitude coordinates of the city center."""
        lat = self.metadata.at[(self.name, 'latitude')]
        lon = self.metadata.at[(self.name, 'longitude')]
        return lat, lon

    @property
    def product_id(self):
        """Landsat product identifier."""
        return self.metadata.at[(self.name, 'product_id')]

    @property
    def profile(self):
        """Raster profile."""
        landsat_path = os.path.join(self.landsat_dir, 'red.tif')
        with rasterio.open(landsat_path) as geotiff:
            profile = geotiff.profile
        profile.update(count=1)
        return profile

    # Accessing data

    @property
    def aoi(self):
        """Area of interest as a GeoJSON-like dictionnary."""
        path = os.path.join(self.intermediary_dir, 'masks', 'aoi.geojson')
        with open(path) as f:
            geojson = json.load(f)
        return geojson['geometry']

    @property
    def roads(self):
        """OSM roads as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'roads.shp')
        return gpd.read_file(path)

    @property
    def buildings(self):
        """OSM buildings as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'buildings.shp')
        return gpd.read_file(path)

    @property
    def leisure(self):
        """OSM leisure as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'leisure.shp')
        return gpd.read_file(path)

    @property
    def landuse(self):
        """OSM landuse as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'landuse.shp')
        return gpd.read_file(path)

    @property
    def natural(self):
        """OSM natural as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'natural.shp')
        return gpd.read_file(path)

    @property
    def seas(self):
        """OSM seas as a geodataframe."""
        path = os.path.join(DATA_DIR, 'input', 'seas', 'seas.shp')
        seas = gpd.read_file(path)
        return seas.to_crs(self.crs)

    @property
    def blocks(self):
        """OSM blocks as a geodataframe."""
        path = os.path.join(self.intermediary_dir, 'osm', 'blocks.shp')
        return gpd.read_file(path)

    @property
    def blocks_raster(self):
        """Rasterized urban blocks."""
        path = os.path.join(self.intermediary_dir, 'osm', 'blocks.tif')
        with rasterio.open(path) as src:
            return src.read(1)

    @property
    def nonbuilt(self):
        """OSM non-built features."""
        path = os.path.join(self.intermediary_dir, 'osm', 'nonbuilt.shp')
        return gpd.read_file(path)

    @property
    def nonbuilt_raster(self):
        """Rasterized non-built features."""
        path = os.path.join(self.intermediary_dir, 'osm', 'nonbuilt.tif')
        with rasterio.open(path) as src:
            return src.read(1)

    @property
    def nonbuilt_tags(self):
        """Mapping between raster values and OSM tag."""
        path = os.path.join(self.intermediary_dir, 'osm', 'nonbuilt_tags.json')
        with open(path) as f:
            return json.load(f)

    @property
    def buildings_cover(self):
        """OSM buildings coverage as a 2D numpy array (raster)."""
        path = os.path.join(self.intermediary_dir, 'osm', 'buildings.tif')
        with rasterio.open(path) as src:
            return src.read(1)

    @property
    def urban_distance(self):
        """OSM-based urban distance as a 2D numpy array (raster)."""
        path = os.path.join(self.intermediary_dir, 'osm', 'urban_distance.tif')
        with rasterio.open(path) as src:
            return src.read(1)

    @property
    def water(self):
        """OSM-based water mask."""
        path = os.path.join(self.intermediary_dir, 'osm', 'water.tif')
        with rasterio.open(path) as src:
            return src.read(1)

    @property
    def reference_builtup(self):
        """Reference built-up polygons as a geodataframe."""
        path = os.path.join(self.reference_dir, 'builtup.shp')
        return gpd.read_file(path)

    @property
    def reference_baresoil(self):
        """Reference bare soil polygons as a geodataframe."""
        path = os.path.join(self.reference_dir, 'baresoil.shp')
        return gpd.read_file(path)

    @property
    def reference_lowveg(self):
        """Reference low vegetation polygons as a geodataframe."""
        path = os.path.join(self.reference_dir, 'lowveg.shp')
        return gpd.read_file(path)

    @property
    def reference_highveg(self):
        """Reference high vegetation polygons as a geodataframe."""
        path = os.path.join(self.reference_dir, 'highveg.shp')
        return gpd.read_file(path)

    @property
    def reference(self):
        """Rasterized reference data set."""
        path = os.path.join(self.intermediary_dir,
                            'reference', 'reference.tif')
        with rasterio.open(path) as src:
            return src.read(1)

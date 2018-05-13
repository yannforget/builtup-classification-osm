"""OpenStreetMap data pre-processing to use it as training data."""

import os
import json
import multiprocessing as mp

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from shapely.geometry import MultiLineString, shape, mapping
from shapely.ops import linemerge
from tqdm import tqdm

import raster as rst
from metadata import CITIES, DATA_DIR, City


# non-built tags
TAGS = [
    'scrub', 'farmland', 'wetland', 'wood', 'park', 'forest',
    'nature_reserve', 'golf_course', 'cemetery', 'sand', 'quarry',
    'pitch', 'scree', 'meadow', 'orchard', 'grass', 'recreation_ground',
    'grassland', 'garden', 'heath', 'bare_rock', 'beach', 'greenfield'
]
# road tags for urban blocks
ROADS = [
    'residential', 'unclassified', 'tertiary', 'living_street', 'road'
]


def nonbuilt_features(leisure, landuse, natural, tags):
    """Get a non-built geodataframe by concatenating the leisure,
    landuse and natural features.

    Parameters
    ----------
    leisure : GeoDataFrame
        OSM leisure polygons.
    landuse : GeoDataFrame
        OSM landuse polygons.
    natural : GeoDataFrame
        OSM natural polygons.
    tags : list of str
        List of OSM tags to include.

    Returns
    -------
    nonbuilt : GeoDataFrame
        Concatenated non-built geodataframe. The column `tag` contains
        the value of the `leisure`, `landuse` or `natural` key.
    """

    def simplify_tag(row):
        """Returns the first encountered non-null tag."""
        for tag in row[['leisure', 'landuse', 'natural']]:
            if not pd.isnull(tag):
                return tag
        return None

    # Merge the three geodataframes
    features = pd.concat([leisure, landuse, natural])
    features = features.assign(tag=features.apply(simplify_tag, axis=1))
    features = features[['geometry', 'tag']]

    # Avoid unwanted tags
    features = features[features.tag.isin(tags)]

    return features


def nonbuilt_raster(nonbuilt, profile):
    """Rasterize OSM non-built features.

    Parameters
    ----------
    nonbuilt : geodataframe
        OSM non-built features in a geodataframe.
    profile : dict
        Main rasterio profile used for rasterization.
    
    Returns
    -------
    nonbuilt_raster : 2D numpy array
        Rasterized non-built features with pixel values equal to the
        non-built tag ID.
    tags_map : dict
        Mapping between tags ID and tag labels.
    """
    # Avoid polygons smaller than a landsat pixel
    nonbuilt = nonbuilt[nonbuilt.area >= 900]

    # Map each tag to an integer ID
    unique_tags = np.unique(nonbuilt.tag)
    tags_map = {tag: i+1 for i, tag in enumerate(unique_tags)}

    # Rasterize
    geoms = [mapping (geom) for geom in nonbuilt.geometry]
    tags = [tags_map[tag] for tag in nonbuilt.tag]
    shapes = ((geom, tag) for geom, tag in zip(geoms, tags))

    nonbuilt_r = rasterio.features.rasterize(
        shapes=shapes,
        fill=0,
        all_touched=False,
        transform=profile['affine'],
        out_shape=(profile['height'], profile['width']),
        dtype=np.uint8
    )

    return nonbuilt_r, tags_map


def urban_blocks(roads, aoi, types_of_roads=None):
    """Extract urban blocks from the road network. Here, blocks are defined as
    the difference between the whole area of interest and the buffered road network.
    Roads and AOI must have the same CRS.

    Parameters
    ----------
    roads : GeoDataFrame
        OSM roads.
    aoi : geometry
        Area of interest as a shapely geometry.
    types_of_roads : list of str
        List of `highway` tags included in the analysis.

    Returns
    -------
    blocks : GeoDataFrame
        Urban blocks as a GeoDataFrame.
    """
    crs = roads.crs

    # Only include the provided road types
    if types_of_roads:
        roads = roads[roads.highway.isin(types_of_roads)]
    
    # Clean the roads geodataframe. If some geometries are
    # MultiLineString, convert them to multiple LineStrings
    def _to_linestrings(geoms):
        lines = []
        for geom in geoms:
            if isinstance(geom, MultiLineString):
                for linestring in geom:
                    lines.append(linestring)
            else:
                lines.append(geom)
        return lines

    # Blocks are the polygons resulting from the difference binary
    # predicate between the AOI and the buffered road network
    geoms = _to_linestrings(roads.geometry)
    geoms = MultiLineString([geom for geom in geoms if geom.is_valid])
    geoms = linemerge(geoms)
    road_network = geoms.buffer(1, resolution=1, cap_style=3)
    geometries = aoi.difference(road_network)

    # Put the geometries into a GeoDataFrame
    dataframe = gpd.GeoDataFrame(
        index=[x for x in range(len(geometries))], columns=['geometry'])
    dataframe.geometry = [geom for geom in geometries]
    dataframe.crs = crs

    return dataframe


def urban_blocks_raster(blocks, profile):
    """Rasterize urban blocks. Pixel values are equal to the surface of
    the block in EPSG units.

    Parameters
    ----------
    blocks : geodataframe
        OSM blocks as returned by `urban_blocks()`.
    profile : dict
        Main rasterio profile used for rasterization.
    
    Returns
    -------
    urban_blocks : 2D numpy array
        Rasterized urban blocks as a 2D numpy array.
    """
    surfaces = blocks.area * 1e-4  # Blocks surfaces in hectares
    surfaces = surfaces.apply(round, ndigits=2)
    blocks = blocks.assign(surface=surfaces)

    shapes = ((mapping(geom), surface) for _, (_, geom, surface) in blocks.iterrows())

    blocks_r = rasterio.features.rasterize(
        shapes=shapes,
        fill=0,
        all_touched=False,
        transform=profile['affine'],
        out_shape=(profile['height'], profile['width']),
        dtype=np.float
    )

    return blocks_r


def buildings_cover(buildings, profile):
    """Rasterize buildings footprints extracted from OpenStreetMap
    according to a given Rasterio profile. Pixel values correspond
    to the coverage of a pixel by any building footprint.

    Parameters
    ----------
    buildings : GeoDataFrame
        OSM buildings footprints.
    profile : dict
        Main rasterio profile used for the rasterization.

    Returns
    -------
    cover : 2D array
        Buildings coverage raster (0-1).
    """
    cover = rst.rasterize(
        buildings, profile, two_steps_scaling=10, dtype=np.float
    )
    return cover


def distance_to_urban(roads, buildings, profile):
    """Compute the distance of each pixel to any road or building extracted
    from OpenStreetMap.

    Parameters
    ----------
    roads : GeoDataFrame
        OSM roads.
    buildings : GeoDataFrame
        OSM buildings.
    profile : dict
        Main rasterio profile used for the rasterization.

    Returns
    -------
    urban_distance : 2D numpy array
        Distance raster (in same unit as input EPSG) as a 2D numpy array.
    """
    roads_raster = rst.rasterize(roads, profile, all_touched=True)
    buildings_raster = rst.rasterize(buildings, profile, all_touched=True)
    urban = roads_raster | buildings_raster
    urban_distance = rst.cdist(urban, profile)
    return urban_distance


def water_mask(natural, seas, profile):
    """Create a raster binary mask of seas and water bodies.

    Parameters
    ----------
    natural : GeoDataFrame
        OSM natural polygons.
    seas : GeoDataFrame
        OSM seas shapefile.
    profile : dict
        Main rasterio profile.

    Returns
    -------
    water : 2D numpy array
        Boolean raster mask (True: water, False: no water).
    """
    water_bodies = natural[natural.natural == 'water']
    water_bodies_r = rst.rasterize(water_bodies, profile, all_touched=True)
    water_bodies_r = water_bodies_r.astype(np.bool)

    seas = seas.to_crs(profile['crs'])
    seas_r = rst.rasterize(seas, profile, all_touched=True)
    seas_r = seas_r.astype(np.bool)

    water = water_bodies_r | seas_r
    return water


def preprocess(city_name):
    """OSM pre-processing for a given case study."""
    city = City(city_name)

    osm_dir = os.path.join(city.intermediary_dir, 'osm')
    mask_dir = os.path.join(city.intermediary_dir, 'masks')

    # OSM non-built shapefile
    out_f = os.path.join(osm_dir, 'nonbuilt.shp')
    if not os.path.isfile(out_f):
        nonbuilt = nonbuilt_features(
            city.leisure, city.landuse, city.natural, TAGS)
        nonbuilt.to_file(out_f)

    # OSM non-built raster and tags map
    raster_f = os.path.join(osm_dir, 'nonbuilt.tif')
    map_f = os.path.join(osm_dir, 'nonbuilt_tags.json')
    if not os.path.isfile(raster_f) or not os.path.isfile(map_f):
        raster, tag_map = nonbuilt_raster(city.nonbuilt, city.profile)
        profile = city.profile.copy()
        profile.update(dtype=raster.dtype.name, nodata=None)
        with rasterio.open(raster_f, 'w', **profile) as dst:
            dst.write(raster, 1)
        with open(map_f, 'w') as f:
            f.write(json.dumps(tag_map, indent=True))

    # OSM urban blocks shapefile
    out_f = os.path.join(osm_dir, 'blocks.shp')
    if not os.path.isfile(out_f):
        blocks = urban_blocks(
            city.roads, shape(city.aoi), types_of_roads=ROADS)
        blocks.to_file(out_f)

    # OSM urban blocks raster
    out_f = os.path.join(osm_dir, 'blocks.tif')
    if not os.path.isfile(out_f):
        blocks = city.blocks
        raster = urban_blocks_raster(blocks, city.profile)
        profile = city.profile.copy()
        profile.update(dtype=raster.dtype.name, nodata=None)
        with rasterio.open(out_f, 'w', **profile) as dst:
            dst.write(raster, 1)

    # OSM buildings raster
    out_f = os.path.join(osm_dir, 'buildings.tif')
    if not os.path.isfile(out_f):
        buildings = buildings_cover(city.buildings, city.profile)
        profile = city.profile.copy()
        profile.update(dtype=buildings.dtype.name)
        with rasterio.open(out_f, 'w', **profile) as dst:
            dst.write(buildings, 1)

    # OSM-based urban distance raster
    out_f = os.path.join(osm_dir, 'urban_distance.tif')
    if not os.path.isfile(out_f):
        urban_distance = distance_to_urban(
            city.roads, city.buildings, city.profile)
        profile = city.profile.copy()
        profile.update(dtype=urban_distance.dtype.name)
        with rasterio.open(out_f, 'w', **profile) as dst:
            dst.write(urban_distance, 1)

    # OSM-based water mask raster
    out_f = os.path.join(osm_dir, 'water.tif')
    if not os.path.isfile(out_f):
        seas_f = os.path.join(DATA_DIR, 'input', 'seas', 'seas.shp')
        seas = gpd.read_file(seas_f)
        water = water_mask(city.natural, seas, city.profile)
        profile = city.profile.copy()
        profile.update(dtype=np.uint8, nodata=None)
        with rasterio.open(out_f, 'w', **profile) as dst:
            dst.write(water.astype(np.uint8), 1)
    
    return

if __name__ == '__main__':

    processes = []

    for city_name in CITIES:
        p = mp.Process(target=preprocess, args=(city_name,))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()

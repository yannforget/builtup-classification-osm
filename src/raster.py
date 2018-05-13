"""Raster processing & reprojection."""

import os
import subprocess

import numpy as np
import rasterio
import rasterio.features
import rasterio.warp


def rescale_profile(profile, scale=5):
    """Rescale a Rasterio profile by calculating a new transform
    and a new shape.

    Parameters
    ----------
    profile : dict
        Input rasterio profile.
    scale : int, optional (default=5)
        Scaling factor.

    Returns
    -------
    profile : dict
        Rescaled rasterio profile.
    """
    new_profile = profile.copy()
    trans = profile['affine']
    trans = rasterio.Affine(
        trans.a / scale, trans.b, trans.c,
        trans.d, trans.e / scale, trans.f)
    new_profile['affine'] = trans
    new_profile['height'] *= scale
    new_profile['width'] *= scale
    return new_profile


def rescale_raster(raster, src_profile, dst_profile,
                   resampling_method='average'):
    """Rescale a raster.

    Parameters
    ----------
    raster : array
        Input raster as a 2D NumPy array.
    src_profile : dict
        Source rasterio profile.
    dst_profile : dict
        Target rasterio profile.
    resampling_method : str, optional (default='average')
        Possible values are 'nearest', 'bilinear', 'cubic', 'cubic_spline',
        'lanczos', 'average', 'mode', 'gauss', 'max', 'min' and 'med'.

    Returns
    -------
    raster : array
        Output raster as a 2D NumPy array.
    """
    method = rasterio.warp.Resampling.__dict__[resampling_method]
    dst_shape = (dst_profile['height'], dst_profile['width'])
    new_array = np.empty(shape=dst_shape)
    rasterio.warp.reproject(
        raster, new_array,
        src_transform=src_profile['affine'],
        dst_transform=dst_profile['affine'],
        src_crs=src_profile['crs'],
        dst_crs=dst_profile['crs'],
        resampling=method)
    return new_array


def rasterize(
        dataframe, profile, all_touched=False,
        two_steps_scaling=0, dtype=np.uint8):
    """Rasterize a GeoPandas dataframe into a binary raster.

    Parameters
    ----------
    dataframe : GeoDataFrame
        Input geopandas.GeoDataFrame.
    profile : dict
        Target rasterio profile.
    all_touched : bool, optional (default=False)
        Consider the whole pixel or only its center for the intersection
        with the input shapes.
    two_steps_scaling : int, optional (default=0)
        If not zero, rasterize at a higher scale and rescale the raster to
        the target spatial resolution by averaging.
    dtype : dtype, optional (default=np.uint8)
        Output raster dtype.

    Returns
    -------
    raster : array
        Output raster as a 2D NumPy array.
    """
    # If DataFrame CRS not assigned, assume it's the same
    # as in the Rasterio profile.
    if not dataframe.crs:
        dataframe.crs = profile['crs']

    # If DataFrame and Raster CRS are different, reproject
    # DataFrame geometries.
    if dataframe.crs != profile['crs']:
        dataframe.to_crs(profile['crs'], inplace=True)

    # Get geometries
    features = ((geom, 1) for geom in dataframe.geometry)

    # Two-steps rasterization:
    #     1) Rasterize at x/k resolution;
    #     2) Average aggregation at x resolution.
    if two_steps_scaling:
        rescaled_profile = rescale_profile(
            profile, scale=two_steps_scaling)
        raster = rasterio.features.rasterize(
            shapes=features, fill=0, all_touched=all_touched,
            transform=rescaled_profile['affine'],
            out_shape=(rescaled_profile['height'], rescaled_profile['width']),
            dtype=dtype)
        return rescale_raster(raster, rescaled_profile, profile)

    # Or simple one-step rasterization
    return rasterio.features.rasterize(
        shapes=features, fill=0, all_touched=all_touched,
        transform=profile['affine'],
        out_shape=(profile['height'], profile['width']),
        dtype=dtype)


def random_choice(raster, size, random_seed=None):
    """Randomly choose a given amount of pixels from a binary raster.
    Unchosen pixels are assigned the value of 0.

    Parameters
    ----------
    raster : array-like
        Input binary raster as a 2D NumPy array.
    size : int
        Number of pixels wanted.

    Returns
    -------
    raster : array-like
        Output raster.
    """
    if np.count_nonzero(raster == 1) == size:
        return raster
    pixels = np.where(raster.ravel() == 1)[0]

    if random_seed:
        np.random.seed(random_seed)

    selected = np.random.choice(pixels, size=size, replace=False, )
    new_data = np.zeros_like(raster.ravel())
    new_data[selected] = 1

    return new_data.reshape(raster.shape).astype(np.bool)


def cdist(src, profile, cache_dir="/tmp"):
    """Get a distance raster, i.e. distance of each pixel to a given class.
    Wrapper around the `gdal_proximity.py` script from GDAL.

    Parameters
    ----------
    src : str
        Input raster path.
    profile : dict
        Rasterio profile for the output raster.
    cache_dir : str, optional (default='/tmp')
        Cache directory where the output raster will be written
        before being passed to Python.

    Returns
    -------
    dist : array
        Output raster as a 2D NumPy array.
    """
    prf = profile.copy()
    prf['dtype'] = str(src.dtype)
    prf['nodata'] = None
    if 'transform' in prf:
        del prf['transform']
    src_fname = os.path.join(cache_dir, 'src_raster.tif')
    dst_fname = os.path.join(cache_dir, 'dst_raster.tif')
    for fname in (src_fname, dst_fname):
        if os.path.isfile(fname):
            os.remove(fname)
    with rasterio.open(src_fname, 'w', **prf) as tif:
        tif.write(src, 1)
    env = {'PATH': os.getenv('PATH')}
    subprocess.run(
        ['gdal_proximity.py', '-distunits', 'GEO', src_fname, dst_fname],
        env=env, stdout=subprocess.DEVNULL)
    with rasterio.open(dst_fname) as tif:
        dist_raster = tif.read(1)
    for fname in (src_fname, dst_fname):
        os.remove(fname)
    return dist_raster


def is_raster(obj):
    """Check if the object is a raster."""
    has_2d = False
    is_array = isinstance(obj, np.ndarray)
    if is_array:
        has_2d = obj.ndim == 2
    return is_array and has_2d


def euclidean_distance(sign_x, sign_y):
    """Compute the euclidean distance between two spectral signatures x and y
    identified by two 1D arrays of length 6 (i.e. the number of Landsat bands).
    """
    squared_differences = (sign_x - sign_y) ** 2
    return np.sqrt(squared_differences.sum())

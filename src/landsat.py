"""Implement Landsat scene as a Python class."""

import os

import numpy as np
import rasterio

BANDS = [
    'blue',
    'green',
    'red',
    'nir',
    'swir1',
    'swir2',
    'tir1',
    'tir2'
]


def calc_ndi(bi, bj):
    """Compute normalized difference index for a given
    couple of bands.
    """
    # Transform input bands so that bi + bj != 0
    if bi.min() < 1:
        bi = bi + np.abs(bi.min()) + 1
    if bj.min() < 1:
        bj = bj + np.abs(bj.min()) + 1
    # Calculate NDI
    ndi = (bi - bj) / (bi + bj)
    return ndi


class Scene(object):
    """Landsat scene."""

    def __init__(self, data_dir):
        """Initialize a new Landsat scene for a given case study.

        Parameters
        ----------
        data_dir : str
            Path to the directory where Landsat bands are stored.
        """
        self.bands = BANDS
        self.dir = data_dir

    def read(self, band_name):
        """Read a band."""
        band_path = os.path.join(self.dir, band_name + '.tif')
        with rasterio.open(band_path) as src:
            return src.read(1)

    @property
    def blue(self):
        """Blue band as a 2D numpy array."""
        return self.read('blue')

    @property
    def red(self):
        """Red band as a 2D numpy array."""
        return self.read('red')

    @property
    def green(self):
        """Green band as a 2D numpy array."""
        return self.read('green')

    @property
    def nir(self):
        """Near-infrared band as a 2D numpy array."""
        return self.read('nir')

    @property
    def swir1(self):
        """Short-wave infrared 1 as a 2D numpy array."""
        return self.read('swir1')

    @property
    def swir2(self):
        """Short-wave infrared 2 as a 2D numpy array."""
        return self.read('swir2')

    @property
    def tir1(self):
        """Thermal infrared 1 as a 2D numpy array."""
        return self.read('tir1')

    @property
    def tir2(self):
        """Thermal infrared 2 as a 2D numpy array."""
        return self.read('tir2')

    @property
    def cfmask(self):
        """CFmask result as a 2D numpy array."""
        return self.read('cfmask')

    @property
    def profile(self):
        """Rasterio profile (dictionnary)."""
        path = os.path.join(self.dir, 'red.tif')
        with rasterio.open(path) as src:
            return src.profile

    def __iter__(self):
        """Iterate over bands."""
        for band_label in self.bands:
            yield getattr(self, band_label)

    def __len__(self):
        """Number of bands."""
        return len(self.bands)

    def __getitem__(self, i):
        """Allow indexing."""
        band_label = self.bands[i]
        return getattr(self, band_label)

    @property
    def ndsv_(self):
        """Get NDSV labels corresponding to all the possible band
        combinations as a list of tuples.
        """
        band_combinations = []
        for i, bi in enumerate(self.bands):
            for j, bj in enumerate(self.bands[i+1:]):
                band_combinations.append((bi, bj))
        return band_combinations

    def calc_ndsv(self):
        """Compute normalized difference spectral vector."""
        nrows, ncols = self.red.shape
        combinations = self.ndsv_

        dst_array = np.zeros(
            shape=(len(combinations), nrows, ncols),
            dtype=np.float
        )

        for v, (bi_label, bj_label) in enumerate(self.ndsv_):
            bi = getattr(self, bi_label).astype(np.float)
            bj = getattr(self, bj_label).astype(np.float)
            ndi = calc_ndi(bi, bj)
            dst_array[v, :, :] = ndi

        return dst_array

    @property
    def ndsv(self):
        """Normalized Difference Spectral Vector. Returns
        cached version if available.
        """
        cache_f = os.path.join(self.dir, 'ndsv.tif')

        # Returns cached version if available...
        if os.path.isfile(cache_f):
            with rasterio.open(cache_f) as src:
                return src.read()

        # ...else compute and cache
        array = self.calc_ndsv()
        ndims = array.shape[0]
        profile = self.profile.copy()
        profile.update(dtype=array.dtype.name, transform=None, count=ndims)
        with rasterio.open(cache_f, 'w', **profile) as dst:
            for i in range(ndims):
                dst.write(array[i, :, :], i+1)

    def signature(self, y):
        """Compute the mean spectral signature of a geographic object identified
        by a binary raster y. TIR bands are ignored.
        """
        spectral_signature = []
        for band, label in zip(self, self.bands):
            if 'tir' in label:
                continue
            band = band / 10000  # Minmax scale (0, 1)
            band_y = band[y]
            spectral_signature.append(band_y.mean())
        return np.array(spectral_signature)

    @property
    def mask(self):
        """Nodata mask."""
        return self.red < 0

    @property
    def water(self):
        """Returns a water mask based on CFMask algorithm."""
        return self.cfmask == 1

    @property
    def clouds(self):
        """Returns cloud mask based on CFMask algorithm."""
        return (self.cfmask == 2) | (self.cfmask == 4)

    # Access some known indexes as class properties

    @property
    def ndvi(self):
        return - self.ndsv[13, :, :]

    @property
    def ndbi(self):
        return - self.ndsv[18, :, :]

    @property
    def ndbal(self):
        return self.ndsv[23, :, :]

    @property
    def mndwi(self):
        return self.ndsv[9, :, :]

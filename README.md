[![DOI](https://zenodo.org/badge/133227237.svg)](https://zenodo.org/badge/latestdoi/133227237)

# Description

This repository contains all the code required to reproduce the results presented in the following paper:

* Y. Forget, C. Linard, M. Gilbert. *Supervised Classification of Built-up Areas in Sub-Saharan African Cities using Landsat Imagery and OpenStreetMap*, 2018.

The results of the study can be explored [here](http://maupp.ulb.ac.be/page/forget2018/) in an interactive map.

Input, intermediary and output data can be downloaded from [zenodo](https://zenodo.org/record/1291961).

# Dependencies

Dependencies are listed in the `environment.yml` file at the root of the repository. Using the [Anaconda](https://www.anaconda.com/download) distribution, a virtual environment containing all the required dependencies can be created automatically:

``` sh
# Clone the repository
git clone https://github.com/yannforget/builtup-classification-osm.git
cd builtup-classification-osm

# Create the Python environment
conda env create --file environment.yml

# Activate the environment
source activate landsat-osm
# Or, depending on the system:
conda activate landsat-osm
```

# Data

Due to storage constraints, input data are not integrated to this repository. However, input and intermediary files required to run the analysis can be downloaded from a [zenodo deposit](https://zenodo.org/record/1291961). Alternatively, output files of the study can be directly downloaded from this repository. To run the following code, input and intermediary files must be downloaded in the `/data` folder. For example, in Linux:

``` sh
# Create the data directory
cd builtup-classification-osm
mkdir data
cd data

# Download input and intermediary data
wget -O input.zip https://zenodo.org/record/1291961/files/input.zip?download=1
wget -O intermediary.zip https://zenodo.org/record/1291961/files/intermediary.zip?download=1

# Decompress the archives
unzip input.zip
unzip intermediary.zip
rm *.zip
```

Likewise, the Global Humans Settlements Layer is required to run the notebook `02-External_Datasets.ipynb`:

``` sh
cd builtup-classification-osm/data/input
wget http://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_LDSMT_GLOBE_R2015B/GHS_BUILT_LDSMT_GLOBE_R2015B_3857_38/V1-0/GHS_BUILT_LDSMT_GLOBE_R2015B_3857_38_v1_0.zip
unzip GHS_BUILT_LDSMT_GLOBE_R2015B_3857_38_v1_0.zip
rm GHS_BUILT_LDSMT_GLOBE_R2015B_3857_38_v1_0.zip
mv GHS_BUILT_LDSMT_GLOBE_R2015B_3857_38_v1_0 ghsl
```

# Code

The code of the analysis in divided in two parts: the Python scripts and modules used to support the analysis, and the notebooks where the outputs of the analysis have been produced.

## Notebooks

* `notebooks/01-Evolution_of_OSM.ipynb` : Analysis of OSM data availability and its evolution from 2011 to 2018. Please note that this analysis requires additionnal files and softwares: the full historic OSM data dump (available through the geofabrik.de website for OpenStreetMap members, and the `osmium` command-line tool).
* `notebooks/02-External_Datasets.ipynb` : Assessment of the GHSL and HBASE datasets in the context of our case studies.
* `notebooks/03-Buildings_Footprints.ipynb` : Assessment of OSM buildings footprints as built-up training samples.
* `notebooks/04-Nonbuilt_Tags.ipynb` : Assessment of OSM non-built polygons (leisure, natural or landuse objects) as non-built-up training samples.
* `notebooks/05-Urban_Blocks.ipynb` : Assessment of OSM-based urban blocks as built-up training samples.
* `notebooks/06-Urban_Distance.ipynb` : Assessment of OSM-based urban distance as non-built-up training samples.
* `notebooks/07-Comparative_Analysis.ipynb` : Supervised classification of built-up areas.

To run the notebooks, `input` and `intermediary` data must have been downloaded (see above). Additionnaly, the following pre-processing scripts must be executed:

``` sh
python src/preprocess_reference.py
python src/preprocess_osm.py
```

The outputs of the other pre-processing scripts are already included in the `intermediary` zenodo archive.

## Scripts

* `src/download_osm.py` : script used for the acquisition of OSM data.
* `src/generate_aoi.py` : script used to generate 40km x 40km area of interest for each case study.
* `src/preprocess_landsat.py` : script used to mask input landsat data according to our areas of interest.
* `src/preprocess_osm.py` : script used to produce the intermediary OSM products: rasterized buildings and non-built objects, urban blocks, urban distance, water mask...
* `src/preprocess_reference.py` : script used to rasterize the reference polygons used as validation data.

## Modules

* `src/metadata.py` : used to access metadata specific to each case study.
* `src/landsat.py` : processing of Landsat data.
* `src/raster.py` : raster processing functions.
* `src/classification.py` : supervised classification and performance assessment.

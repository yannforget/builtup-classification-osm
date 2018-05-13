---
title: "Supervised Classification of Built-up Areas in Sub-Saharan African
Cities using Landsat Imagery and OpenStreetMap"
author: "Yann Forget, Catherine Linard, Marius Gilbert"
affiliation: "Spatial Epidemiology Lab, Université Libre de Bruxelles, Belgium"
keywords: "urban remote sensing; openstreetmap; landsat; crowd-sourced geographic information; sub-saharan africa"
bibliography: "/home/yann/Work/Bibliography/zotero.bib"
abstract: "The Landsat archives have been made freely available in 2008,
allowing the production of high resolution built-up maps at the regional or
global scales. In this context, most of the classification algorithms rely on
supervised learning to tackle the heterogeneity of the urban environments.
However, at large scales, the process of collecting training samples become a
huge project in itself. This leads to a growing interest from the remote sensing
community toward Volunteered Geographic Information (VGI) projects such as
OpenStreetMap (OSM). Despite the spatial heterogeneity of its contribution
patterns, OSM provides an increasing amount of information on the earth's
surface. More interestingly, the community has recently moved beyond street
mapping to collect a wider range of spatial data such as buildings footprints,
land use, or points of interest. In this paper, we propose a classification
method that makes use of OSM to automatically collect training samples for
supervised learning of built-up areas. To take into account a wide range of
issues that could be encountered, the approach is assessed in ten sub-Saharan
African urban areas from various demographic profiles and climates. The obtained
results are compared with (1) existing 30m global urban maps such as the Global
Human Settlements Layer (GHSL) or the Human Built-up and Settlements Extent
(HBASE), and (2) a supervised classification based on manually digitized
training samples. The results suggest that automated supervised classifications
based on OSM can provide performances similar to manual approaches, provided
that OSM training samples are sufficiently available and correctly
pre-processed. Moreover, the proposed method could reach better results in the
near future, given the increasing amount and variety of information in the OSM
database."
link-citations: true
csl: remote-sensing-of-environment.csl
cleveref: on
xnos-capitalise: true
geometry: margin=3cm
fontsize: 10pt
numbersections: true
---

# Introduction

The population of Africa is predicted to double by 2050 [@UN-Habitat2014],
driving a rapidly growing urbanization. In this context, reliable information on
the distribution and the spatial extent of human settlements is crucial to
understand and monitor a large set of associated issues, such as the impacts on
both environmental systems and human health [@Grimm2008; @Dye2008; @Wentz2014].
In the 2000s, the remote sensing community took advantage of the availability of
coarse-resolution satellite imagery based on the MERIS or the MODIS programs in
order to produce global land cover maps such as GlobCover [@Arino2007] or the
MODIS 500m Map of Global Urban Extent (MOD-500) [@Schneider2009]. Subsequently,
Landsat data have been made freely available in 2008 and dramatically reduced
the operative cost of high resolution satellite imagery acquisition and
processing [@Wulder2008]. This enabled the production of high resolution global
land cover maps based on the Landsat catalog, such as the Global Human
Settlements Layer (GHSL) [@Pesaresi2016b], Global Land Cover (GLC) [@Chen2015]
or the Human Built-up and Settlements Extent (HBASE) [@Wang2017].

However, land cover classification in urban areas remains a challenge because of
the inherent complexity of the urban environment which is characterized by both
intraurban and interurban heterogeneity [@Herold2004; @Small2005]. Considering
the complexity associated with the urban mosaic at high resolution, researchers
are shifting towards the use of supervised classification methods [@Gamba2009a;
@Li2014; @Belgiu2016]. However, such approach requires a large amount of
training samples to grasp the heterogeneity of the urban environment. As a
result, the process of collecting training samples for large-scaled supervised
classification becomes a huge project in itself. Additionally, studies have
shown that global urban maps suffer from higher rates of misclassifications in
developing regions such as sub-Saharan Africa or South Asia [@Potere2009]
because of the lack of reference data in both quantity and quality.

The training samples collection step can be automated by using existing land
cover information in ancillary data sets. Coarser resolution global maps such
as GlobCover or MOD-500 has been widely used to identify training sites
[@Potere2009; @Trianni2015]. However integrating such data sets leads to the
introduction of noisy samples which have been shown to decrease classifiers
performance. More recently, researchers started to investigate the potential of
Voluntereed Geographic Information (VGI) for training samples collection
[@JokarArsanjani2013; @Pesaresi2016b]. Defined as the spatial dimension of the
web phenomenon of user-generated content [@Goodchild2007], VGI drives a new way
of collecting geographic information that relies on the crowd rather than
official and commercial organizations [@JokarArsanjani2015b]. In the recent
years, VGI has known an exponential growth through its more prominent project:
OpenStreetMap (OSM). Initially focused on the mapping of the road network, the
contributors have since enlarged their focus by collecting a wider range of
spatial data such as buildings footprints, points of interest, or land use
features. As a result, and as the database grows, OSM becomes increasingly
relevant to support the training of large-scaled land cover classifications.
However, global VGI projects also bring new issues to consider,
including (1) the spatial heterogeneity of the contribution patterns across the
regions, (2) its non-exhaustive nature, and (3) the lack of global agreement on
the *tagging* process.

Despite the large range of opportunities that OSM offers to support large-scaled
supervised land cover classifications, few studies have investigated its full
potential. This paper focuses on the use of OSM to collect training samples for
the classification of built-up and non-built-up areas in the context of ten
sub-Saharan African urban agglomerations. To support global urban
mapping, our research aims to answer the following questions: What information
can be extracted from the OSM database to collect built-up and non-built-up
training samples? What post-processing must be applied? What performance loss
can we expect compared to a strategy based on a manually digitized dataset? And,
finally, what is the practicability of such approach in the context of a
developing region such as sub-Saharan Africa?

# Material and methods

## Case studies

As stated previously, the spectral profiles of urban areas are characterized by
high interurban variations caused by environmental, historical, or socioeconomic
differences [@Small2005]. This makes the selection of case studies a crucial
step when seeking to ensure the generalization abilities of a method. Our set of
case studies is comprised of ten sub-Saharan African cities described in
{@tbl:case-studies}. Climate is one of the most important source of variation
among the urban areas of the world because it determines the abundance and the
nature of the vegetation in the urban mosaic and at its borders. Urban areas
located in tropical or subtropical climates (Antananarivo, Johannesburg,
Chimoio, Kampala) can be spectrally confused with vegetated areas because of the
presence of dense vegetation in the urban mosaic. This can lead to a mixed-pixel
problem and result in misclassifications. On the contrary, cities located in
arid or semi-arid climates (Dakar, Gao, Katsina, Saint-Louis, Windhoek) are
characterized by a low amount of vegetation. Bare soil being spectrally similar
to built-up, the separation between built-up and non-built-up classes can be
more difficult in such areas [@Zhang2015; @Li2017], especially when construction
materials are made up from nearby natural resources. Population of an urban area
impacts both the distribution of built-up and the data availability. In the
context of our study, the population is mainly used as a proxy of the spatial
contribution patterns of OSM. Highly populated urban areas (Dakar, Johannesburg,
Nairobi, Kampala) are more likely to benefit from a high density of information
in OSM. On the other hand, smaller cities (Chimoio, Gao, Saint-Louis, Windhoek)
can suffer from a lack of OSM contributions.

|   **City**   | **Country**  |   **Climate**[^1]    | **Population**[^2] |
| :----------- | :----------- | :------------------- | -----------------: |
| Antananarivo | Madagascar   | Subtropical highland |          2,452,000 |
| Chimoio      | Mozambique   | Humid subtropical    |            462,000 |
| Dakar        | Senegal      | Hot semi-arid        |          3,348,000 |
| Gao          | Mali         | Hot desert           |            163,000 |
| Johannesburg | South Africa | Subtropical highland |          4,728,000 |
| Kampala      | Uganda       | Tropical rain forest |          3,511,000 |
| Katsina      | Nigeria      | Hot semi-arid        |          1,032,000 |
| Nairobi      | Kenya        | Temperate oceanic    |          5,080,000 |
| Saint-Louis  | Senegal      | Hot desert           |            305,000 |
| Windhoek     | Namibia      | Hot semi-arid        |            384,000 |

Table: Environmental and demographic characteristics of the case studies. {#tbl:case-studies}

[^1]: According to the Köppen-Geiger classification.

[^2]: According to the AfriPop dataset [@Linard2012b].

## Imagery

The Landsat 8 imagery is provided by the U.S. Geological Survey (USGS) through
the Earth Explorer portal. The scenes are acquired as Level-1 data products,
therefore radiometrically calibrated and orthorectified. Calibrated digital
numbers are converted to surface reflectance values using the Landsat Surface
Reflectance Code (LaSRC) [@Vermote2016] made available by the USGS. Clouds,
cloud shadows and water bodies are detected using the Function of Mask (FMASK)
algorithm [@Zhu2012; @Zhu2015]. The acquisition dates range from August 2015 to
October 2016, because of availability issues caused by cloud cover. In order to
reduce the processing cost of the analysis, the satellite images are masked
according to an area of interest (AOI), which is defined as the extent of a 20
kilometers buffer around the city center (as provided by OSM). As a result, all
AOI have a surface of $40 km \times 40 km$.

|   **City**   |           **Landsat Product ID**           |  **Date**  |
| :----------- | :----------------------------------------- | :--------- |
| Antananarivo | `LC08_L1TP_159073_20150919_20170404_01_T1` | 2015–09–19 |
| Chimoio      | `LC08_L1TP_168073_20150529_20170408_01_T1` | 2015–05–29 |
| Dakar        | `LC08_L1TP_206050_20151217_20170331_01_T1` | 2015–12–07 |
| Gao          | `LC08_L1TP_194049_20160114_20170405_01_T1` | 2016–01–14 |
| Johannesburg | `LC08_L1TP_170078_20150831_20170404_01_T1` | 2015–08–31 |
| Kampala      | `LC08_L1TP_171060_20160129_20170330_01_T1` | 2016–01–29 |
| Katsina      | `LC08_L1TP_189051_20160111_20170405_01_T1` | 2016–01–11 |
| Nairobi      | `LC08_L1TP_168061_20160124_20170330_01_T1` | 2016–01–24 |
| Saint-Louis  | `LC08_L1TP_205049_20161009_20170320_01_T1` | 2016–10–09 |
| Windhoek     | `LC08_L1TP_178076_20160114_20170405_01_T1` | 2016–01–14 |

Table: Landsat 8 imagery. {#tbl:landsat-imagery}

## Reference dataset

Reference samples for four land cover classes are collected using very high
spatial resolution (VHSR) imagery from Google Earth: built-up, bare soil, low
vegetation (sparse vegetation, farms) and high vegetation (forests). Even if our
classification problem is binary (built-up vs. non-built-up), the collection of
reference samples for specific land covers was preferred to ensure the spectral
representativeness of the non-built-up landscape. As shown in
{@fig:ref-samples}, samples were collected as polygons in order to include the
inherent spectral heterogeneity of urban land covers. Reference built-up areas
deliberately included mixed pixels provided that they contain at least 20% of
built-up.

In total, more than 2400 polygons were digitized, corresponding to more than
180,000 pixels after rasterization. In the context of our case study, reference
samples were used for (1) assessing the quality of the training samples
extracted from OSM, (2) assessing the performance of the built-up
classifications, and (3) producing a reference classification for comparison
purposes.

![Examples of digitized reference samples in Dakar, Senegal: __a)__ Built-up, __b)__ Bare soil, __c)__ Low vegetation, __d)__ High vegetation.](figures/dakar_ref_samples.pdf){#fig:ref-samples}

## OpenStreetMap

OSM data have been acquired in January 2018 using the Overpass API. Five
different objects are collected from the database: (1) `highway` polylines (the
road network), (2) `building=yes` polygons (the buildings footprints), (2) the
`landuse`, `leisure`, and `natural` polygons (potentially non-built-up objects),
and (4) `natural=water` polygons (the water bodies).

Spatial contribution patterns of OSM are not homogeneous [@JokarArsanjani2015].
Users are more likely to contribute information in their own geographic area.
Therefore, highly populated urban areas benefit from more mapping effort in OSM
compared to small rural areas. Furthermore, because of the _"Digital
Divide"_ [@Goodchild2007] caused by inequalities in access to education and
internet, developing and developed countries does not benefit from the same
amount of contributions. As of march 2018, the European continent includes ten
times the amount of information (in bytes) of Africa in the OSM database.
Another example of such heterogeneity is that Germany contains two times more
bytes of information than sub-Saharan Africa. However, as shown in
{@fig:osm-continents}, OSM is increasingly relevant in developing regions. As a
matter of fact, Africa is the continent where contributions are increasing at
the higher rate since 2014.

![Bytes of information in the OSM database for each
continent.](figures/osm_per_continent.pdf){#fig:osm-continents width=500px}

The evolution of OSM data availability for each type of objects in each case
study is shown in {@fig:osm-local}. The trends observed at the continental scale
are confirmed in the context of our case studies. Street mapping appears as a
continuous effort and leads to a linear increase of the number of roads in the
database. However, some highly populated urban areas such as Katsina still
suffer from a lack of contributions. As suggested by its name, OSM was initially
focused on street mapping. Later, contributors started to integrate buildings
footprints, points of interest, or land use and land cover features. As a
result, the number of buildings footprints, natural and land use polygons has
more than doubled between 2016 and 2018. These trends suggest that OSM can
support large-scaled supervised classification in developing regions. They also
reveal that an increasing amount of data will be available in the near future.

![Evolution of OSM data availability in our case studies between 2011 and
2018.](figures/osm_history_local.pdf){#fig:osm-local}

## Training samples

### Built-up samples

In the OSM database, the `building` key is used to mark an area as a building.
When they are available, the buildings footprints are the perfect candidates for
built-up training samples collection thanks to their unambiguous spatial
definition. However, as shown in @{fig:buildings-availability}, they are not
consistently available among the cities. Highly populated urban areas such as
Nairobi, Dakar or Johannesburg contain more than 1,000 hectares of buildings
footprints, whereas smaller cities such as Katsina and Gao only contain a few of
them, thus reducing the representativeness of the full built-up spectral
signature. Such data availability issue implies that additional samples must
be collected from another data source. {fig:buildings-availability} also reveals
that the typical building footprint does not cover more than 15% of the surface
of a Landsat pixel. It means that, when going from the vector space to the 30m
raster space of our analysis, the geographic object is not the building
footprint anymore but the percentage of the pixel which is effectively covered
by any footprint. As a result, the decision to include or exclude a pixel from
the built-up training samples relies on a binary threshold, under the assumption
that the higher the threshold, the lower the risk is to include mixed pixels.

![Availability and median surface of buildings footprints in each case
study.](figures/buildings_availability.pdf){#fig:buildings-availability}

As previously stated, OSM buildings footprints are not a sufficient data source
to collect built-up training samples because of inconsistencies in data
availability among cities. The main focus of the OSM project is still *street
mapping*, thereby the road network is the most exhaustive feature in the
database. Even the smallest cities among our case studies contain hundreds of
kilometers of roads, and new streets are being mapped each month. As illustrated
in {@fig:blocks-windhoek}, built-up information can be derived from these road
networks using the concept of urban blocks, defined as the polygons shaped by
the intersection of the roads. In order to focus on residential blocks, only
roads tagged as `residential`, `tertiary`, `living_street`, `unclassified` or
with the generalist `road` tag were used. Major roads such as highways, express
ways or national roads were avoided, as well as service roads, tracks, and paths.
In the case of Katsina and Gao, for which the buildings footprints did not
provide a sufficient amount of built-up training samples, the process resulted in
the availability of more than 1000 blocks. One assumption can be made regarding
the reliability of such geographic objects to collect more built-up training
samples: large blocks have a higher probability of containing mixed pixels or
non-built-up areas.

![Urban blocks extracted from the OSM road network in Windhoek, Namibia. Red
blocks have a surface greater than 1 hectare. Green blocks have a surface lower
than 1 hectare. Satellite imagery courtesy of
Google.](figures/blocks_windhoek.png){#fig:blocks-windhoek}

### Non-built-up samples

Because of the focus of the OSM database on the urban objects, the extraction of
non-built-up samples was less straightforward than the extraction of built-up
samples. The OSM database includes information on the physical materials at the
surface of the earth according to: (1) the description of various bio-physical
landscape features such as grasslands or forests with the `natural` key, (2) the
primary usage for an area of land such as farms, or managed forests and
grasslands with the `landuse` key, and (3) the mapping of specific leisure
features such as parks or nature reserves with the `leisure` key. Such objects
are not ensured to be non-built-up and must be filtered according to their
assigned tag. From the 105 available tags for our case studies, the following 20
tags were selected: `sand`, `farmland`, `wetland`, `wood`, `park`,
`forest`, `nature_reserve`, `golf_course`, `cemetery`, `sand`, `quarry`,
`pitch`, `scree`, `meadow`, `orchard`, `grass`, `recreation_ground`,
`grassland`, `garden`, `heath`, `bare_rock`, `beach` and `greenfield`. 

However, the availability of non-built objects was not consistent among the case
studies. Antananarivo, Johannesburg, Kampala, or Nairobi contained more than 1000
non-built-up objects according to the previously stated definition. On the
contrary, smaller cities such as Chimoio or Katsina benefited from less than 50
objects. Given the spectral and spatial heterogeneity of the non-built landscape
which may consist of different types of soil and vegetation, a low amount of
non-built-up objects may induce a lack of representativeness in the training
dataset. Still, a large amount of urban information is available through the
road network or the digitized buildings footprints. In cases of low OSM data
availability, this information allows for the discrimination of areas with a low
probability of being built-up. The underlying assumption is that the areas which
are distant from any urban object, such as any road or building,
have a low probability of being built-up, thereby making potential candidates for
being used as non-built-up training samples. Under the previous assumptions, we
define the urban distance as the distance from any road or building, such as:

$$ d_{urban} = \min ( d_{roads} , d_{buildings} ) $$ {#eq:urban-distance}

### Samples quality assessment

To assess the quality of the training samples extracted from the OSM database,
we measured the distance between their spectral signatures and those of the
reference land cover polygons. The spectral signature of an object is the
variation of its reflectance values according to the wavelength. In the six
non-thermal Landsat bands, the spectral signature $S$ of an object can be
defined as:

$$ S = ( \bar{x}_1,\ \ldots \ ,\ \bar{x}_n \ ,\  \ldots \ ,\ \bar{x}_6 ) $$ {#eq:spectral-signature}

with $\bar{x}_n$ being the mean pixel value of the object for the band $n$.
Therefore, the euclidean spectral distance $d$ between two objects $x$ and $y$
can be defined as:

$$ d(x,y) = \sqrt{\sum\limits_{i=1}^{n=6} ( \bar{x}_i - \bar{y}_i )^2} $$ {#eq:spectral-distance}

More specifically, the optimal value of four parameters was investigated: (1)
the minimum coverage threshold for the building footprints, (2) the maximum
surface threshold for the urban blocks, (3) the accepted OSM tags for
non-built-up objects, and (4) the minimum distance threshold for random
selection of supplementary non-built-up samples from the urban distance raster. 

## Classification

Relying on crowd-sourced geographic information to automatically generate a
training data set implies that the resulting sample will be more noisy compared
to a manual sampling strategy. Therefore, a larger amount of samples may be
required to compensate the mislabeled points and the lack of representativeness.
Consequently, the binary classification task (built-up vs. non-built) was
performed using the Random Forest (RF) classifier, which has been shown to be
computationally efficient and relatively robust to outliers and noisy training
data [@Rodriguez-Galiano2012; @Mellor2015]. The implementation was based on a
set of Python libraries, including: NumPy and SciPy for scientific computing,
Rasterio for raster processing, Shapely and Geopandas for vector analysis, and
Scikit-learn [@Pedregosa2011] for machine learning.

In order to remove errors and ambiguities caused by variations in acquisition
conditions, the 8 input Landsat bands were transformed to a Normalized
Difference Spectral Vector (NDSV) [@Angiuli2014] before the classification. The
NDSV is a combination of all normalized spectral indices, as defined in
{@eq:ndi} and {@eq:ndsv}. In the case of Landsat, this leads to a vector of 28
normalized spectral indices.

$$ f(b_i, b_j) = \frac{b_i - b_j}{b_i + b_j} $$ {#eq:ndi}

$$ NDSV = \begin{bmatrix} f(b_1, b_2) \\ \dots \\ f(b_i, b_j) \\ \dots \\ f(b_7, b_8) \end{bmatrix} $$ {#eq:ndsv} 

To assess the use of OSM for supervised built-up classification, a comparative
approach was adopted. Three distinct classifications have been carried out using
different training datasets, as described in {@tbl:schemes}. A reference
classification ($REF$) was performed using the reference land cover polygons as
training samples in order to assess the relative performance of OSM-based
approaches. In this case, reference polygons have been randomly split between a
training and a testing dataset of equal sizes. The procedure was repeated 20
times and the validation metrics were averaged. Training samples of the two
other classifications ($OSM_a$ and $OSM_b$) were exclusively extracted from OSM.
The first one used first-order features from OSM: buildings footprints as
built-up samples, and landuse, natural and leisure polygons as non-built-up
samples. The second one was designed to tackle the OSM data availability issue
which may be encountered in less populated urban areas. It made use of
second-order features derived from first-order objects such as urban blocks and
urban distance. 

|         |      Built-up training samples      |     Non-built-up training samples     |
| ------- | ----------------------------------- | ------------------------------------- |
| $REF$   | Reference built-up polygons         | Reference non-built-up polygons       |
| $OSM_a$ | Buildings footprints                | Non-built-up objects                  |
| $OSM_b$ | Buildings footprints & Urban blocks | Non-built-up objects & Urban distance |

Table: Training samples data sources for each classification scheme. {#tbl:schemes}

In all three cases, RF parameters have been set according to the recommendations
of the literature [@Rodriguez-Galiano2012; @Mellor2015]. RF decision tree
ensembles were constructed with 100 trees, and the maximum number of features
per tree was set to the square root of the total number of features. Imbalance
issues between built-up and non-built-up training datasets sizes were tackled by
over-sampling the minority class [@Lemaitre2017]. Additionally, fixed random
seeds were set to ensure the reproducibility of the analysis.

# Validation

Classification performances were assessed using the manually digitized reference land cover polygons as a testing dataset. Three validation metrics were computed: F1-score, precision and recall. In order to assess the classification performances in specific areas, accuracy scores in the four available land covers (built-up, bare soil, low vegetation, high vegetation) were also computed. The metrics are computed for the three classifications, as well as for two existing Landsat-based urban maps: the GHSL and the HBASE datasets.

# Results and Discussion

## Built-up training samples

The extraction of built-up training samples from the OSM buildings footprints required the selection of a minimum coverage threshold. The impact of this threshold has been assessed by measuring the spectral distance of the resulting samples to the reference built-up samples. As shown in {@fig:buildings-mincov}, the assumption that increasing the threshold would minimize the spectral distance to the reference built-up is not verified. Indeed, the highest spectral distances are reached when only fully covered pixels are selected. This reveals the importance of maximizing the representativeness of the sample by ensuring that a sufficient amount of samples is available. Furthermore, given the non-exhaustive nature of the OSM database, a pixel that contains a building footprint of any size have a high probability to contain additional unmapped built-up structures. However, low threshold values (between 0 and 0.2) appear to effectively increase the spectral similarity with the reference built-up samples by eliminating pixels covered by small and isolated buildings. Overall, a minimum coverage threshold of 0.2 appears to maximize both samples quality and quantity.

![Quality and quantity of built-up training samples extracted from OSM building footprints according to the minimum coverage threshold in the 10 case studies: __a)__ mean spectral distance to the reference built-up samples, __b)__ mean number of samples (in pixels).](figures/buildings_mincov.pdf){#fig:buildings-mincov}

Urban blocks enabled the collection of built-up training samples where buildings footprints were lacking. {@fig:blocks-maxsurface} shows the impact of the maximum surface threshold on both samples quality and quantity. As expected, excluding large blocks increases the spectral similarity with the reference built-up samples by avoiding highly mixed pixels and bare lands. The highest similarity is reached when only including the blocks with a surface lower than 1 hectare. However, this conservative threshold dramatically reduces the sample size in small urban agglomerations such as Katsina, Gao, or Saint-Louis. Therefore, a maximum surface threshold of 3 hectares has been selected in order to ensure a sufficient amount of samples while minimizing the spectral distance to the reference built-up samples.

![Quality and quantity of built-up training samples extracted from OSM urban blocks according to maximum surface threshold in the 10 case studies: __a)__ mean spectral distance to the reference built-up samples, __b)__ number of samples (in pixels) in the 5 case studies with the lowest data availability.](figures/urban_blocks.pdf){#fig:blocks-maxsurface}

## Non-built-up training samples

The non-built-up landscape is spectrally complex due to its irregular spatial
patterns and the variations of soils and vegetation types.
{@fig:nonbuilt-similarity} shows the most similar land cover of each OSM
non-built-up tag in terms of spectral distance. The analysis reveals the
spectral variability of OSM non-built-up objects across the case studies. Urban
features such as `garden`, `recreation_ground`, `pitch` or `park` can have a
spectral signature closer to built-up than to bare soil or lowly vegetated
areas. The small surface covered by these features can lead to a high proportion
of mixed pixels. Additionally, their urban nature makes highly probable the
presence of human-constructed elements. On the contrary, natural features such
as `orchard`, `meadow`, `forest` or `wood` are more consistently close to the
spectral signature of vegetated areas. Generally, most of the features providing
bare soil samples may be confused with built-up areas because of their urban
nature (`pitch`) or their spectral similarity (`beach`). However, the decision
boundary between built-up and bare soil pixels being the most prone to errors in
urban areas, we choose to not exclude them in order to maximize the
representativeness. Overall, these inconsistencies also highlight the fact that
a supervised multi-class land cover classification based on OSM would be
difficult to set up as of today.

![Most similar land cover of each OSM non-built-up object according to its tag. Circles are logarithmically proportional to the number of pixels available.](figures/nonbuilt_similarity.pdf){#fig:nonbuilt-similarity}

In case studies where OSM non-built-up objects were not sufficiently available,
an urban distance raster was used to randomly collect supplementary training
samples in remote areas. {@fig:urbandist} shows the relationship between the
remoteness and the spectral distance to the reference built-up samples. As
expected, the spectral distance increases with the urban distance. However, the
spectral variations become inconsistent and are mainly caused by changes in the
non-built-up landscape (e.g. forests, mountains, or bare lands). In highly
urbanized agglomerations such as Johannesburg or Dakar, the road network covers
the whole area of interest, leading to a very low amount of remote pixels.
Consequently, a minimum distance threshold of 250m was used.

![Quality and quantity of non-built-up training samples extracted from the OSM-based urban distance raster: __a)__ mean spectral distance to the reference built-up samples according to the urban distance, __b)__ number of samples (in pixels) in the 5 case studies with the lowest sample availability.](figures/urban_distance.pdf){#fig:urbandist}

## GHSL and HBASE assessment

The assessment metrics for the GHSL and HBASE data sets in the context of our case studies are shown in {@tbl:external-scores}. They are provided as an indication of their relevance in the context of our case studies and our definition of a built-up area. They also reveal which case studies may be problematic for an automated built-up mapping method. For example, the arid urban area of Gao suffers from low recall scores because of the spectral confusion that occurs between the buildings materials and the bare surroundings areas. This leads to the misclassification of large built-up areas as bare lands. To a lesser extent, the semi-arid urban areas of Saint-Louis, Windhoek, Dakar and Katsina present the same issue. On the contrary, subtropical urban areas such as Antananarivo or Chimoio are characterized by an abundant vegetation in the urban mosaic. Thus, high rates of misclassifications are observed in the peripheral areas where built-up is less dense. A similar phenomenon is also noticed in the richest residential districts of Johannesburg. Overall, both data sets reach a mean F1-score of 0.82 when excluding Gao.


|              |          | *GHSL*    |        |          | *HBASE*   |        |
| :----------- | :------: | :-------: | :----: | :------: | :-------: | :----: |
|              | F1-score | Precision | Recall | F1-score | Precision | Recall |
| Antananarivo | 0.83     | 0.82      | 0.83   | 0.79     | 0.67      | 0.96   |
| Chimoio      | 0.47     | 0.97      | 0.31   | 0.82     | 0.94      | 0.73   |
| Dakar        | 0.85     | 0.74      | 1.00   | 0.81     | 0.69      | 0.98   |
| Gao          | 0.35     | 0.98      | 0.21   | 0.73     | 0.94      | 0.59   |
| Johannesburg | 0.92     | 0.86      | 0.99   | 0.9      | 0.82      | 1.00   |
| Kampala      | 0.96     | 0.95      | 0.96   | 0.95     | 0.93      | 0.97   |
| Katsina      | 0.9      | 0.92      | 0.88   | 0.65     | 0.76      | 0.56   |
| Nairobi      | 0.84     | 0.96      | 0.75   | 0.88     | 0.81      | 0.97   |
| Saint-Louis  | 0.76     | 0.95      | 0.63   | 0.81     | 0.97      | 0.7    |
| Windhoek     | 0.81     | 0.92      | 0.73   | 0.78     | 0.65      | 0.99   |
| Mean         | 0.77     | 0.91      | 0.73   | 0.81     | 0.82      | 0.84   |
| Std. Dev.    | 0.19     | 0.07      | 0.26   | 0.08     | 0.12      | 0.17   |

Table: Assessment metrics for the GHSL and HBASE datasets. {#tbl:external-scores}

## Classification results

Assessment metrics of the three classification schemes are presented in
{@tbl:classification-scores}. The reference classification, which has been
trained with manually digitized samples, reached a mean F1-score of 0.92 and a
minimum of 0.84 in Gao. Such results suggest that high classification
performances can be achieved in most of the case studies provided that the
training dataset is sufficiently large and representative. The first OSM-based
classification scheme ($OSM_a$) made use of first-order OSM objects: buildings
footprints and objects associated with a non-built up tag. Therefore, a limited
availability in either of the aforementioned objects was highly detrimental to
the classification performance. Katsina, Windhoek, and Johannesburg suffered
from a low availability in buildings footprints with respectively 110, 2636, and
6724 objects. This led to an unrepresentative built-up training sample
consisting mainly of large administrative structures or isolated settlements. In
Chimoio, more than 150,000 buildings footprints were available. However, only 12
non-built-up polygons have been extracted from the OSM database, all related to
forested areas. As a result, the lack of information regarding the spectral
characteristics of the heterogeneous non-built-up landscape had not enabled the
separation between built-up and bare areas. A similar issue was also encountered
in Antananarivo, where most of the non-built-up training samples were located in
natural reserves and forests. 

The second OSM-based classification scheme ($OSM_b$) was designed to tackle the
aforementioned issues by deriving second-order features from the road network.
The addition of built-up and non-built-up training samples collected from urban
blocks and remote areas solved the data availability and representativeness
issues in all the case studies, leading to better scores in 9 cases. Overall,
$OSM_b$ reached scores that were comparable to those of the reference
classification. More specifically, $OSM_b$ had the highest recall scores,
suggesting that the model was more successfull in the detection of isolated,
informal or peripheral settlements. Additionally, the use of larger training
datasets (from 30,000 to 500,000 samples per case study) led to higher
consistencies in the classification performance with a standard deviation of
0.02.


|              |        | $OSM_a$ |       |        | $OSM_b$ |       |        | $REF$ |       |
| :----------- | :----: | :-----: | :---: | :----: | :-----: | :---: | :----: | :---: | :---: |
|              | F1-sc. |  Prec.  | Rec.  | F1-sc. |  Prec.  | Rec.  | F1-sc. | Prec. | Rec.  |
| Antananarivo |  0.78  |  0.99   | 0.65  |  0.93  |  0.91   | 0.96  |  0.92  | 0.97  | 0.87  |
| Chimoio      |  0.77  |  0.63   | 0.97  |  0.92  |  0.90   | 0.95  |  0.85  | 0.93  | 0.79  |
| Dakar        |  0.95  |  0.98   | 0.92  |  0.96  |  0.94   | 0.98  |  0.94  | 0.98  | 0.90  |
| Gao          |  0.81  |  0.96   | 0.69  |  0.90  |  0.94   | 0.86  |  0.84  | 0.84  | 0.86  |
| Johannesburg |  0.60  |  0.98   | 0.43  |  0.92  |  1.00   | 0.86  |  0.96  | 0.98  | 0.94  |
| Kampala      |  0.98  |  1.00   | 0.97  |  0.98  |  0.99   | 0.96  |  0.98  | 0.99  | 0.96  |
| Katsina      |  0.20  |  0.84   | 0.11  |  0.91  |  0.95   | 0.87  |  0.94  | 0.99  | 0.90  |
| Nairobi      |  0.91  |  0.94   | 0.89  |  0.94  |  0.97   | 0.92  |  0.93  | 0.97  | 0.89  |
| Saint-Louis  |  0.95  |  0.98   | 0.93  |  0.94  |  0.92   | 0.96  |  0.92  | 0.98  | 0.88  |
| Windhoek     |  0.68  |  0.98   | 0.52  |  0.95  |  0.93   | 0.98  |  0.93  | 0.96  | 0.90  |
| Mean         |  0.76  |  0.93   | 0.71  |  0.93  |  0.94   | 0.93  |  0.92  | 0.96  | 0.89  |
| Std. Dev.    |  0.22  |  0.11   | 0.27  |  0.02  |  0.03   | 0.05  |  0.04  | 0.04  | 0.04  |

Table: Assessment metrics for the three classification schemes. {#tbl:classification-scores}

With $OSM_b$, three case studies still had a recall scores lower than 0.9: Gao,
Johannesburg and Katsina. This suggests that the model did not effectively
detect built-up in some areas. {@fig:misclassifications} shows some examples of
such areas. In Katsina, higher rates of misclassifications were observed in the
north-east part of the city, where urban vegetation was denser that in other
parts of the agglomeration. Furthermore, because of a less dense road network
and the unavailability of buildings footprints, no training samples were
available in this area. Likewise, the richest neighborhoods in Johannesburg are
characterized by isolated buildings in a denser urban vegetation, leading to a
higher rate of misclassification. In Gao, errors were mainly caused by the
spectral confusion which occurred between built-up and bare soil areas. The
phenomenon was exacerbated by the arid climate and the buildings materials made
off nearby natural resources.

![Areas with high rates of misclassifications in __a)__ Katsina, __b)__ Johannesburg, __c)__ Gao and __d)__ Dakar.](figures/misclassifications.pdf){#fig:misclassifications}

Generally, as shown in {@fig:n-samples}, the classification scores increased
with the number of training samples. Because of the introduction of noise and
mislabaled samples inherent to automated approaches, large training datasets
were required to make sense of the heterogeneous spectral characteristics of the
urban environment. {@fig:n-samples} suggests that between 10,000 and 20,000
samples are necessary to fit the classification model depending on the spectral
complexity of the urban mosaic.

![Relationship between the number of training samples and the classification F1-score (The outlier Johannesburg is excluded from the graph).](figures/n_samples_fit.pdf){#fig:n-samples}

# Conclusion

The study provided important insights regarding the automation of training
samples collection to support large-scaled or rapid supervised classification of
built-up areas. The proposed method made use of the growing amount of
information in the OSM database to automatically extract both built-up and
non-built-up training samples. The method can reach similar classification
performances than when using manual approaches, provided that a relevant set of
pre-processing routines are applied. In some less populated urban areas,
first-order urban features (such as building footprints) can be too scarce. The
issue can be tackled by a spatial analysis of the road network to derive
second-order features such as urban blocks or urban distance. The proposed
approach reached a mean F1-score of 0.93 across our case studies, while the
manual approach reached 0.92.

Automatically generated training data sets contain more noise than when manually
collected. Additionally, relying on crowd-sourced geographic information
introduces its own share of errors and inconsistencies. Previous studies have
shown that the RF classifier can handle up to 20% of noise in the training data
set, provided that the sample size is large enough [@Mellor2015]. Overall, these
previous findings are confirmed by our results. In our case studies, maximizing
the size of the training data set was more advantageous that minimizing the
noise.

Land use and land cover mapping in the OSM community is a relatively new
phenomenon, especially in developing countries. As a matter of fact, 77% of the
buildings footprints and 50% of the land use polygons used in this study has
been mapped after January 2016. The growing amount of available data suggests
that the proposed approach will provide better results in the following years.
More importantly, the mapping of land use and natural elements could enable
multi-class supervised land cover classifications in the near future.

# References

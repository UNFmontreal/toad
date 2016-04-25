# Tractometry
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractometry                            |
|**Goal**        | Remove outliers |
|**Config file** | qryDict` <br> `qryFile` <br> `ignore`|
|**Time**        | About 5 minutes                                         |
|**Output**      | -  Each bundles extracted from tractquerier <br>|

#

## Goal

The tractfiltering step remove outliers from bundles previously extracted.


## Requirements

- Clean tractogram file (trk) for each bundle of interest

## Config files parameter

Configuration file to remove outliers

- `configTractometry: configTractometry_default.json`

- `ignore: False`

## Implementation

### 1- Tractometry

<a href="http://tract-querier.readthedocs.org/en/latest/" target="_blank">WMQL documentation</a>

### 2- Use your own queries and atlases

If you want to use your own configuration file you need to add it in your backup or raw folder. It has to start with 'configTractFiltering' with a 'json' extension. You can find an example in /usr/local/toad/template/tractometry/configTractFiltering_default.json

## Expected result(s) - Quality Assessment (QA)

It creates two folders:
- outlier_cleaned_tracts: each bundle extracted
- outliers: each bundle extracted:

Production of an image (png) for each example for the QA in order to check the results.

## References

### Associated documentation

- <a href="http://scil.dinf.usherbrooke.ca/wp-content/papers/cote-etal-ismrm15.pdf" target="_blank">Tract Filtering</a>

### Articles 

- TractFiltering

> Cousineau, M., E. Garyfallidis, M-A. Cote, P-M. Jodoin, and M. Descoteaux. (2016) Tract-profiling and bundle statistics: a test-retest validation study. Proceedings of: International Society of Magnetic Resonance in Medicine (ISMRM), Singapore (2016).



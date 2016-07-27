# Tractometry
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractometry                            |
|**Goal**        | Remove outliers |
|**Config file** | `ignore`|
|**Time**        | About 5 minutes                                         |
|**Output**      | -  Each bundles extracted from tractquerier <br>|

#

## Goal

The tractometry step compute metric from HARDI and Tensor reconstruction along the bundles previously extracted.


## Requirements

- Clean tractogram file (trk) for each bundle of interest

## Config files parameter

Configuration file to remove outliers

- `configTractometry: configTractometry_default.json`

- `ignore: False`

## Implementation

### 1 - Tractometry

scil_run_tractometry function (If you need more information send a message to toadunf.criugm@gmail.com)

## Expected result(s) - Quality Assessment (QA)

It creates two folders:
- outlier_cleaned_tracts: each bundle extracted
- outliers: each bundle extracted:

Production of an image (png) for each example for the QA in order to check the results.

## References

### Associated documentation

- <a href="http://scil.dinf.usherbrooke.ca/wp-content/papers/cote-etal-ismrm15.pdf" target="_blank">Tractometry</a>

### Articles 

- Tractometry

> Cousineau, M., E. Garyfallidis, M-A. Cote, P-M. Jodoin, and M. Descoteaux. (2016) Tract-profiling and bundle statistics: a test-retest validation study. Proceedings of: International Society of Magnetic Resonance in Medicine (ISMRM), Singapore (2016).



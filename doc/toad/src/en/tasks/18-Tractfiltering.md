# TractFiltering
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractfiltering                                    |
|**Goal**        | Remove outliers |
|**Config file** | `ignore`|
|**Time**        | About 5 minutes                                         |
|**Output**      | -  Each bundles extracted from tractquerier <br>|

#

## Goal

The tractfiltering step remove outliers from bundles previously extracted.

## Requirements

- Tractogram file (trk) for each bundle of interest

## Config files parameter

Configuration file to remove outliers

- `configTractFiltering: configTractFiltering_default.json`

- `ignore: False`

## Implementation

### 1- TractFiltering

- function: scil_run_tractometry (If you need more information send a message to toadunf.criugm@gmail.com)

### 2- Use your own queries and atlases

If you want to use your own configuration file you need to add it in your backup or raw folder. It has to start with **configTractFiltering** with a **.json** extension. You can find an example in /usr/local/toad/template/tractometry/configTractFiltering_default.json

## Expected result(s) - Quality Assessment (QA)

It creates two folders:

- outlier_cleaned_tracts: each bundle extracted
- outliers: streamlines that have been removed

Production of an image (png) for each example for the QA in order to check the results.

## References

### Associated documentation

- <a href="http://scil.dinf.usherbrooke.ca/wp-content/papers/cote-etal-ismrm15.pdf" target="_blank">Tract Filtering</a>

### Articles 

- TractFiltering

> Cousineau, M., E. Garyfallidis, M-A. Cote, P-M. Jodoin, and M. Descoteaux. (2016) Tract-profiling and bundle statistics: a test-retest validation study. Proceedings of: International Society of Magnetic Resonance in Medicine (ISMRM), Singapore (2016).



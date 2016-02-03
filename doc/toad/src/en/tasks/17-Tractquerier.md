# TractQuerier
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractquerier                                    |
|**Goal**        | Select automatically bundles of streamlines using White Matter Query Language (WMQL) |
|**Config file** | `atlas` <br> `qryDict` <br> `qryFile` <br> `ignore`|
|**Time**        | About 5 minutes                                         |
|**Output**      | -  Each bundles asked in the query <br>|

#

## Goal

The tractquerier step extract specific bundles of streamlines using WMQL .


## Requirements

- Tractogram file (trk)
- Atlas (wmparc, brodmann, aal2)

## Config files parameter

- `atlas: wmparc`

Atlas used to segment bundles of streamlines

- `qryDict: Freesurfer.qry`

Desired number of tracks

- `qryFile: query_freesurfer.qry`

Downsample factor to reduce output file size

- `ignore: False`

## Implementation

### 1- Tract_querier 

<a href="http://tract-querier.readthedocs.org/en/latest/" target="_blank">WMQL documentation</a>

## Expected result(s) - Quality Assessment (QA)

It creates a file for each bundle of the query file.

Production of an image (png) for each example for the QA in order to check the results.

## References

### Associated documentation

- <a href="https://github.com/demianw/tract_querier" target="_blank">WMQL</a>


### Articles 

- Tract_querier 

> The white matter query language: a novel approach for describing human white matter anatomy", Wassermann et al. Brain Structure and Function 2016



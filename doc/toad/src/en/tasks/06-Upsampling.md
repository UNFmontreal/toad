# Upsampling
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Upsampling                                            |
|**Goal**        | Upsampling of the diffusion-weigthed images           |
|**Config file** | `voxel_size` <br /> `cleanup`                         |
|**Time**        | Few minutes                                           |
|**Output**      | Diffusion-weighted upsampled images                   |

# 

## Goal

The upsampling task creates diffusion-weighted images (DWI) upsampled to anatomical image resolution

## Requirements

- Diffusion-weigthed images (dwi)

## Config file parameters

Upsampling voxel size in x y z direction suited for upsampling

- `voxel_size: 1 1 1`

Remove extra files

- `cleanup: True`

## Implementation

### 1- Upsampling

<a href="https://github.com/MRtrix3/mrtrix3/wiki/mrconvert" target="_blank">mri_convert</a>

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weighted upsampled images
- Creation of an image (png) of DWI and an image (png) of the b0 


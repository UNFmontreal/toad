# Hardimrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | hardimrtrix                                    |
|**Goal**        | Perform constrain spherical deconvolution using MRtrix dwi2fod |
|**Parameters**  | `ignore`|
|**Time**        | N/A        |
|**Output**      | Fiber orientation distribution (fod, csd) <br> Number of fibers orientations (nufo) <br> |

## Goal

Hardimrtrix step reconstruct fiber orientation distribution (fod) using non-negativity constrained spherical deconvolution (csd) from diffusion-weigthed images (dwi). This step uses dwi2fod command line from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix</a>]

## Default paramaters

We provide default parameters as they are suggested in <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix wiki</a>

## Config file parameters

Ignore hardimrtrix task: **not recommended**
- `ignore: False`


## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Get response from a single population fiber

- [dwi2response](https://github.com/MRtrix3/mrtrix3/wiki/dwi2response)

### 2- Perform spherical deconvolution

- [dwi2fod](https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod)

### 3- Extract fixelPeaks and number of fiber orientation map 

- [fod2fixel](https://github.com/MRtrix3/mrtrix3/wiki/fod2fixel)
- [fixel2voxel](https://github.com/MRtrix3/mrtrix3/wiki/fixel2voxel)


## Expected result(s) - Quality Assessment (QA)

- Creation of the fiber orientation distribution (fod) and metrics (nufo, peaks)
- PNG of the number of fibers orientations (nufo)

## References

### Scientific articles

Tournier, J. D., Calamante, F., & Connelly, A. (2007). Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. *NeuroImage*.

### Associated documentation
- [MRtrix dwi2fod](https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod)

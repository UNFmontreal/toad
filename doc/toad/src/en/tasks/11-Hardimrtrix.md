# Hardimrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | hardimrtrix                                    |
|**Goal**        | Perform constrain spherical deconvolution using MRtrix dwi2fod |
|**Parameters**  | `ignore`|
|**Time**        | N/A        |
|**Output**      | Fiber orientation distribution (fod, csd) <br> Number of fibers orientations (nufo) <br> |

#

## Goal

The hardimrtrix step reconstructs fiber orientation distribution (fod) using non-negativity constrained spherical deconvolution (csd) from diffusion-weigthed images (dwi). 
This step uses the `dwi2fod` command from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix</a>]

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

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2response" target="_blank">dwi2response</a>

### 2- Perform spherical deconvolution

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">dwi2fod</a>

### 3- Extract fixelPeaks and number of fiber orientation map 

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/fod2fixel" target="_blank">fod2fixel</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/fixel2voxel" target="_blank">fixel2voxel</a>

## Expected result(s) - Quality Assessment (QA)

- Creation of the fiber orientation distribution (fod) and metrics (nufo, peaks)
- Produce an image (png) of the number of fibers orientations (nufo)

## References

### Associated documentation

<a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix dwi2fod</a>

### Articles

- Tournier, J. D., Calamante, F., & Connelly, A. (2007). Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. *NeuroImage, 35(4)*, 1459-1472. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/17379540" target="_blank">Link to the article</a>]

# Tensorfsl
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensorfsl                                    |
|**Goal**        | Reconstruction of the tensor using FSL dtifit                                    |
|**Parameters**  | Diffusion-weigthed images (dwi) <br> Diffusion-weighted gradient scheme (b or bvec and bval)|
|**Time**        | N/A        |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3)<br> Mode of the anisotropy (mo) <br> Raw T2 signal with no diffusion weighting (so) <br> Sum of square errors (sse) |

## Goal

Tensorfsl step reconstruct tensors from diffusion-weigthed images and extract tensor metrics such as fractional anisotropy (fa) or mean diffusivity (md). This step uses dtfit command line from FSL [ref: <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT" target="_blank">FSL</a>]


## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Reconstruction of the tensor

```{.python}
function: cmd = "dtifit -k {} -o {} -r {} -b {} --save_tensor --sse ".format(source, target, bVecs, bVals)
```

### 2- Creation of the radial diffusivity

```{.python}
function: self.__mean(l2, l3, rd)
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- Creation of the sum of square error map (sse)
- PNG of principal metrics (fa. ad, rd and md) and PNG of the sse

## References



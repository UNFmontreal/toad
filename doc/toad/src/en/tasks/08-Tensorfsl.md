# Tensorfsl
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensorfsl                                             |
|**Goal**        | Reconstruction of the tensor using FSL dtifit         |
|**Config file** | `ignore`                                              |
|**Time**        | N/A                                                   |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3)<br> Mode of the anisotropy (mo) <br> Raw T2 signal with no diffusion weighting (so) <br> Sum of square errors (sse) |

#

## Goal

The tensorFSL step reconstructs the tensors from the diffusion-weigthed images and then extracts the tensor metrics such as fractional anisotropy (FA) or mean diffusivity (MD).
This step uses `dtfit` command from FSL [ref: <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT" target="_blank">FSL</a>]

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Config file parameters

Ignore tensorfsl task: not recommended
- `ignore: False`

## Implementation

### 1- Reconstruction of the tensor

- [dtifit](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/fdt/UserGuide#DTIFIT)

### 2- Creation of the radial diffusivity

```{.python}
function: self.__mean(l2, l3, rd)
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- Creation of the sum of square error map (sse)
- Produce an image (png) of the principal metrics (FA, AD, RD and MD) and an image (png) of the SSE

## References

### Associated documentation

- [FSL wiki](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT)

### Scientific articles

- Smith, S. M., Jenkinson, M., Woolrich, M. W., Beckmann, C. F., Behrens, T. E. J., Johansen-Berg, H., Bannister, P. R., et al. (2004). Advances in functional and structural MR image analysis and implementation as FSL. *NeuroImage, 23 Suppl 1, S208-19*. [[Link to the article](http://www.sciencedirect.com/science/article/pii/S1053811904003933)]



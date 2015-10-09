# Tensordipy
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensordipy                                   |
|**Goal**        | Reconstruction of the tensor using dipy |
|**Parameters**  | `ignore`|
|**Time**        | N/A        |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3) |

## Goal

Tensordipy step reconstruct tensors from diffusion-weigthed images and extract tensor metrics such as fractional anisotropy (fa) or mean diffusivity (md). This step uses dtfit command line from dipy [ref: <a href="http://nipy.org/dipy/examples_built/reconst_dti.html#example-reconst-dti" target="_blank">dipy</a>]

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (bvec and bval)
- Mask of the brain (optional)

## Config file

Ignore tensordipy task: **not recommended**
- `ignore: False`

## Implementation

### 1- Reconstruction of the tensor

[reconst_dti](http://nipy.org/dipy/examples_built/reconst_dti.html#example-reconst-dti)

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- PNG of principal metrics (fa. ad, rd and md)

## References

Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. *Biophysical journal, 66(1)*, 259-67. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1275686&tool=pmcentrez&rendertype=abstract

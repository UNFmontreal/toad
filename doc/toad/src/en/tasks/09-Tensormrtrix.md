# Tensormrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensormrtrix                                    |
|**Goal**        | Reconstruction of the tensor using MRtrix dwi2tensor                                    |
|**Parameters**  | `modulate` <br> `ignore`|
|**Time**        | N/A        |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3)<br> Mode of the anisotropy (mo) <br> Raw T2 signal with no diffusion weighting (so) <br> Sum of square errors (sse) |

## Goal

Tensormrtrix step reconstruct tensors from diffusion-weigthed images and extract tensor metrics such as fractional anisotropy (fa) or mean diffusivity (md). This step uses dtfit command line from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor" target="_blank">MRtrix</a>]

## Config file

- Method used to fit the tensor: non-linear (check MRtrix default parameters)<br>
- Strength of the regularisation term on the magnitude of the tensor elements: 5000 (check MRtrix default parameters)

Specify how to modulate the magnitude of the eigenvectors {none, FA, eval}
- `modulate: FA`

Ignore tensormrtrix task: not recommended
- `ignore: False`

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Reconstruction of the tensor

- [dwi2tensor](https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor)

### 2- Creation of metrics from tensor

- [tensor2metric](https://github.com/MRtrix3/mrtrix3/wiki/tensor2metric)
- [mrmath](https://github.com/MRtrix3/mrtrix3/wiki/mrmath)

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- Produce an image (png) for each metric (fa. ad, rd and md)

## References

### Scientific articles
- Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. *Biophysical journal, 66(1)*, 259-67. [[Link to the article](http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1275686&tool=pmcentrez&rendertype=abstract)]

### Associated documentation

- [MRtrix dwi2tensor](https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor){:target="_blank"}

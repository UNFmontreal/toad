# Tensormrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensormrtrix                                          |
|**Goal**        | Reconstruction of the tensor using MRtrix dwi2tensor  |
|**Config file** | `ìter` <br> `modulate` <br> `ignore`                              |
|**Time**        | About 10 minutes                                      |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3)<br> Mode of the anisotropy (mo) <br> Raw T2 signal with no diffusion weighting (so)|

#

## Goal

The tensormrtrix step reconstructs tensors from diffusion-weighted images and extracts tensor metrics such as fractional anisotropy (FA) or mean diffusivity (MD). 
This step uses the `dwi2tensor` command line from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor" target="_blank">MRtrix</a>]

## Config file

Number of iterations for estimation of the tensor using WLS - default 2 if 0 then ordinary LS

- `iter: 2`

Specify how to modulate the magnitude of the eigenvectors {none, FA, eval}

- `modulate: FA`

Ignore tensormrtrix task: not recommended

- `ignore: False`

## Requirements

- Diffusion-weighted images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Production of of the mask of the brain (optional)

## Implementation

### 1- Reconstruction of the tensor

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor" target="_blank">dwi2tensor</a>

### 2- Creation of metrics from tensor

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tensor2metric" target="_blank">tensor2metric</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/mrmath" target="_blank">mrmath</a>

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- Produce an image (png) for each metric (fa. ad, rd and md)

## References

### Associated documentation

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor" target="_blank">MRtrix dwi2tensor</a>

### Articles

- Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. *Biophysical journal, 66(1)*, 259-267. [<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1275686&tool=pmcentrez&rendertype=abstract" target="_blank">Link to the article</a>]



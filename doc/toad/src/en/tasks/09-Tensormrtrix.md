# Tensormrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tensormrtrix                                    |
|**Goal**        | Reconstruction of the tensor using MRtrix dwi2tensor                                    |
|**Parameters**  | Diffusion-weigthed images (dwi) <br> Diffusion-weighted gradient scheme (b or bvec and bval)|
|**Time**        | N/A        |
|**Output**      | Tensor image <br> Fractional anisotropy (fa) <br> Mean diffusivity (md) <br> Axial diffusivity (ad) <br> Radial diffusivity (rd) <br> 1st, 2nd and 3rd eigenvector (v1, v2 and v3) <br> 1st, 2nd and 3rd value (l1, l2 and l3)<br> Mode of the anisotropy (mo) <br> Raw T2 signal with no diffusion weighting (so) <br> Sum of square errors (sse) |

## Goal

Tensorfsl step reconstruct tensors from diffusion-weigthed images and extract tensor metrics such as fractional anisotropy (fa) or mean diffusivity (md). This step uses dtfit command line from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2tensor" target="_blank">MRtrix</a>]

## Default paramaters

- Method used to fit the tensor: non-linear <br>
- Strength of the regularisation term on the magnitude of the tensor elements: 5000

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Reconstruction of the tensor

```{.python}
function: cmd = "dwi2tensor {} {} -grad {} -nthreads {} -quiet ".format(source, tmp, encodingFile, self.getNTreadsMrtrix())
```

### 2- Creation of metrics from tensor

```{.python}
function: cmd1 = "tensor2metric {} -adc {} -fa {} -num 1 -vector {} -value {} -modulate {} -nthreads {} -quiet ".format(source, adc, fa, vector, adImage , modulate, self.getNTreadsMrtrix())
function: cmd2 = "tensor2metric {} -num 2 -value {} -modulate {} -nthreads {} -quiet ".format(source, value2, modulate, self.getNTreadsMrtrix())
function: cmd3 = "tensor2metric {} -num 3 -value {} -modulate {} -nthreads {} -quiet ".format(source, value3, modulate, self.getNTreadsMrtrix())

cmd = "mrmath {} {} mean {} -nthreads {} -quiet ".format(value2, value3, rdImage, self.getNTreadsMrtrix())
cmd = "mrmath {} {} {} mean {} -nthreads {} -quiet ".format(adImage, value2, value3, mdImage, self.getNTreadsMrtrix())
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the tensor and metrics
- PNG of principal metrics (fa. ad, rd and md)

## References

Basser, P. J., Mattiello, J., & LeBihan, D. (1994). MR diffusion tensor spectroscopy and imaging. *Biophysical journal, 66(1)*, 259-67. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=1275686&tool=pmcentrez&rendertype=abstract

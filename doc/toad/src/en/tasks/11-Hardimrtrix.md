# Hardimrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | hardimrtrix                                    |
|**Goal**        | Perform constrain spherical deconvolution using MRtrix dwi2fod |
|**Parameters**  | Diffusion-weigthed images (dwi) <br> Diffusion-weighted gradient scheme (b or bvec and bval)|
|**Time**        | N/A        |
|**Output**      | Fiber orientation distribution (fod, csd) <br> Number of fibers orientations (nufo) <br> |

## Goal

Hardimrtrix step reconstruct fiber orientation distribution (fod) using non-negativity constrained spherical deconvolution (csd) from diffusion-weigthed images (dwi). This step uses dwi2fod command line from MRtrix [ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix</a>]

## Default paramaters

We provide default parameters as they are suggested in <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix wiki</a>

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Get response from a single population fiber

```{.python}
function: outputDwi2Response = self.__dwi2response(dwi, wmMask, bFile)
```

### 2- Perform spherical deconvolution

```{.python}
function: self.__dwi2csd(dwi, outputDwi2Response, mask, bFile, self.buildName(dwi, "csd"))
```

### 3- Extract fixelPeaks and number of fiber orientation map 
- ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/fod2fixel" target="_blank">MRtrix fod2fixel</a>
- ref: <a href="https://github.com/MRtrix3/mrtrix3/wiki/fixel2voxel" target="_blank">MRtrix fixel2voxel</a>

```{.python}
function: fixelPeak = self.__csd2fixelPeak(csdImage, mask, self.buildName(dwi, "fixel_peak", 'msf'))
function: self.__fixelPeak2nufo(fixelPeak, mask, self.buildName(dwi, 'nufo'))
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the fiber orientation distribution (fod) and metrics (nufo, peaks)
- PNG of the number of fibers orientations (nufo)

## References

Tournier, J. D., Calamante, F., & Connelly, A. (2007). Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. *NeuroImage*.

## Highly suggested readings

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/dwi2fod" target="_blank">MRtrix wiki</a>
- References

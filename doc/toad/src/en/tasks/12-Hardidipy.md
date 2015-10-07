# Hardidipy
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Hardidipy                                    |
|**Goal**        | Perform constrain spherical deconvolution using Dipy  |
|**Parameters**  | Diffusion-weigthed images (dwi) <br> Diffusion-weighted gradient scheme (bvec and bval)|
|**Time**        | N/A        |
|**Output**      | Fiber orientation distribution (fod, csd) <br> Number of fibers orientations (nufo) <br> |

## Goal

Hardidipy step reconstruct fiber orientation distribution (fod) using non-negativity constrained spherical deconvolution (csd) from diffusion-weigthed images (dwi). [ref: <a href="http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd" target="_blank">Dipy</a>]

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (bvec and bval)
- Mask of the brain (optional)

## Implementation

### 1- Get response from a single population fiber

```{.python}
function: response, ratio = dipy.reconst.csdeconv.auto_response(gradientTable, dwiData, roi_radius=10, fa_thr=0.7)
```

### 2- Perform spherical deconvolution

```{.python}
function: csdModel = dipy.reconst.csdeconv.ConstrainedSphericalDeconvModel(gradientTable, response)
```

### 3- Extract general fractional anisotropy (gfa) and number of fibers orientations (nufo)

```{.python}
function: gfa = csdPeaks.gfa
function: csdCoeff = csdPeaks.shm_coeff
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the fiber orientation distribution (fod) and number of fibers orientations (nufo)
- PNG of the number of fibers orientations (nufo)

## References

Tournier, J. D., Calamante, F., & Connelly, A. (2007). Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. *NeuroImage*.

## Highly suggested readings

- <a href="http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd" target="_blank">Dipy example</a>
- References

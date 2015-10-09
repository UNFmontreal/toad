# Hardidipy
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Hardidipy                                    |
|**Goal**        | Perform constrain spherical deconvolution using Dipy  |
|**Parameters**  | `triangulated_spheres` <br> `ignore`|
|**Time**        | N/A        |
|**Output**      | Fiber orientation distribution (fod, csd) <br> Number of fibers orientations (nufo) <br> |

## Goal

Hardidipy step reconstruct fiber orientation distribution (fod) using non-negativity constrained spherical deconvolution (csd) from diffusion-weigthed images (dwi). [ref: <a href="http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd" target="_blank">Dipy</a>]

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (bvec and bval)
- Mask of the brain (optional)

## Config file parameters

Sphere tesselation {symmetric362, symmetric642, symmetric724, repulsion724, repulsion100} (default=symmetric724)
- `triangulated_spheres: symmetric724`

Ignore hardidipy task: not recommended
- `ignore: False`

## Implementation

### 1- Get response from a single population fiber

- [auto_response](http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd)

### 2- Perform spherical deconvolution

- [reconst_csd](http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd)

### 3- Extract general fractional anisotropy (gfa) and number of fibers orientations (nufo)

```{.python}
function: gfa = csdPeaks.gfa
function: csdCoeff = csdPeaks.shm_coeff
```

## Expected result(s) - Quality Assessment (QA)

- Creation of the fiber orientation distribution (fod) and number of fibers orientations (nufo)
- PNG of the number of fibers orientations (nufo)

## References

### Associated documentation

- <a href="http://nipy.org/dipy/examples_built/reconst_csd.html#example-reconst-csd" target="_blank">Dipy example</a>

### Scientific articles

Tournier, J. D., Calamante, F., & Connelly, A. (2007). Robust determination of the fibre orientation distribution in diffusion MRI: Non-negativity constrained super-resolved spherical deconvolution. *NeuroImage*.

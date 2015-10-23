# Correction
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Correction                                            |
|**Goal**        | Motion and distortion correction of dwi images        |
|**Config file** | `phase_enc_dir` <br> `echo_spacing` <br> `epi_factor` <br> `ignore` <br> `cost` <br> `dof` <br> `interp` <br> `applyxfm` <br> `smooth3`                             |
|**Time**        | About 1 hour                                          |
|**Output**      | Diffusion-weighted images corrected <br> Diffusion-weighted gradient scheme corrected|

#

## Goal

The correction step creates diffusion-weighted images (DWI) corrected for motion. 
If a fielmap or two b0 with opposite PE are provided, the correction step will use them to correct for geometrical distortion as well.


## Minimal Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Optimal Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Two b0s with opposite PE (highly recommended)
or
- Fieldmap (phase and magnitude images)

## Config file parameters

Phase encoding direction.  {0 = P>>A, 1 = A>>P, 2 = R>>L, 3 = L>>R}

- `phase_enc_dir:`

Echo spacing values of the diffusion image (DWI) in ms

- `echo_spacing:`

EPI factor value

- `epi_factor:`

Ignore eddy correction task: **not recommended**

- `ignore: False`

**if fieldmap is provided:**

Cost function from a range of inter- and intra-modal functions {mutualinfo,corratio,normcorr,normmi,leastsq,labeldiff,bbr} (default=corratio)

- `cost: normmi`

Number of transform degrees of freedom (default is 12)

- `dof: 6`

Flirt final interpolation interp {trilinear, nearestneighbour, sinc, spline}  (def=trilinear)

- `interp: nearestneighbour`

Applies transform (no optimisation): requires -init

- `applyxfm: True`

Fugue -s,--smooth3	apply 3D Gaussian smoothing of sigma N (in mm)

- `smooth3: 2.00`

## Implementation

### 1- With two b0s PE (highly recommended)

```{.python}
function: self.__createAcquisitionParameterFile('topup')
function: self.__createAcquisitionParameterFile('eddy')
```

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy" target="_blank">FSL Eddy</a>

### 2- With fieldmap images (phase and magnitude)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
function: self.__computeFieldmap(eddyCorrectionImage, bVals, mag, phase, norm, parcellationMask, freesurferAnat)
```

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy" target="_blank">FSL Eddy</a>

### 3- Without fieldmaps or b0s (with opposite PE)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
```

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy" target="_blank">FSL Eddy</a>

## Expected result(s) - Quality Assessment (QA)

- Motion and geometric distortion DWI corrected
- Diffusion-weighted gradient scheme corrected
- Creation of a gif of dwi before and after correction step
- Creation of a gif of diffusion-weighted gradient scheme before and after correction
 
## References

### Articles

Andersson, J. L. R., Skare, S., & Ashburner, J. (2003). How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. *NeuroImage, 20(2)*, 870-888. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/14568458" target="_blank">Link to the article</a>]


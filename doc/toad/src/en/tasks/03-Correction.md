# Correction
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Correction                                            |
|**Goal**        | Motion and distortion correction of dwi images        |
|**Config file** | `phase_enc_dir` <br />`echo_spacing`<br />`b02b0_filename`<br />`acqp_topup`<br />`acqp_eddy` <br />`index_filename` <br />`topup_results_base_name` <br />`topup_results_output` <br /> |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weighted images corrected <br> Diffusion-weighted gradient scheme corrected|

#

## Goal

The correction step creates diffusion-weighted images (DWI) corrected for motion. 
If a fielmap or two b0 with opposite PE are provided, the correction step will use them to corerct for geometrical distortion as well.


## Minimal Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Optimal Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Two b0s with opposite PE (highly recommended)
or
- Fieldmap (phase and magnitude images)

## Implementation

### 1- With two b0s PE (highly recommended)

```{.python}
function: self.__createAcquisitionParameterFile('topup')
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)
```

### 2- With fieldmap images (phase and magnitude)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, None, indexFile, acqpEddy, bVecs, bVals)
function: self.__computeFieldmap(eddyCorrectionImage, bVals, mag, phase, norm, parcellationMask, freesurferAnat)
```

### 3- Without fieldmaps or b0s (with opposite PE)

```{.python}
function: self.__createAcquisitionParameterFile('eddy')
function: self.__correctionEddy2(dwi, mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)
```

## Expected result(s) - Quality Assessment (QA)

- Motion and geometric distortion DWI corrected
- Diffusion-weighted gradient scheme corrected
- Creation of a gif of dwi before and after correction step
- Creation of a gif of diffusion-weighted gradient scheme before and after correction
 






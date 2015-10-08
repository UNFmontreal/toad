# Registration
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Registration                                          |
|**Goal**        | Registration of the anatomical on diffusion-weighted images |
|**Config file** | `cleanup`                                             |
|**Time**        | N/A                                                   |
|**Output**      | - Anatomical images (resample) <br> - 5tt (resampled, registered) <br> - norm (resampled, registered) <br> - mask (resampled, registered) <br> - aparc_aseg (resampled, registered) <br> - left, right ribbon (resampled, registered)|

#

## Goal

The registration step overlays the anatomical image and atlases on the diffusion-weigthed images. 

## Requirements

- Diffusion-weigthed images (dwi)
- Anatomical image (anat)
- 5tt, norm, mask, aparc_aseg and left right ribbon from parcellation step (Freesurfer pipeline) 

## Config file parameters

[what are the options in the config file -- see parameters in the table]

If anatomical and diffusion-weigthed images were acquired during the same acquisition session we use -usesqform -dof 6

## Implementation

### 1- Compute matrix  

```R
function: freesurferToDWIMatrix = self.__freesurferToDWITransformation(b0, norm, extraArgs)
function: mrtrixMatrix = self.__transformFslToMrtrixMatrix(anat, b0, freesurferToDWIMatrix)
```

### 2- Resample

```R
function: self.__applyResampleFsl(anat, b0, freesurferToDWIMatrix, self.buildName(anat, "resample"))
function: self.__applyResampleFsl(tt5, b0, freesurferToDWIMatrix, self.buildName(tt5, "resample"),True)
function: self.__applyResampleFsl(norm, b0, freesurferToDWIMatrix, self.buildName(norm, "resample"),True)
function: self.__applyResampleFsl(mask, b0, freesurferToDWIMatrix, self.buildName(mask, "resample"),True)

function: self.__applyResampleFsl(aparcAsegFile, b0, freesurferToDWIMatrix, self.buildName(aparcAsegFile, "resample"), True)
function: self.__applyResampleFsl(lhRibbon, b0, freesurferToDWIMatrix, self.buildName(lhRibbon, "resample"),True)
function: self.__applyResampleFsl(rhRibbon, b0, freesurferToDWIMatrix, self.buildName(rhRibbon, "resample"),True)

function: self.__applyResampleFsl(brodmann, b0, freesurferToDWIMatrix, self.buildName(brodmann, "resample"), True)

```

### 3- Registration

```R
function: self.__applyRegistrationMrtrix(tt5, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(norm, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(mask, mrtrixMatrix)

function: self.__applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)

function: self.__applyRegistrationMrtrix(brodmann, mrtrixMatrix)

```

## Expected result(s) - Quality Assessment (QA)

- Produce an image (png) of the B0 overlayed by brain mask and its boundaries
- Produce an image (png) of the B0 overlayed by aparc_aseg file and by the boundaries of the brain mask



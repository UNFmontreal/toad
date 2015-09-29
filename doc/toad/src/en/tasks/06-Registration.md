# Registration
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Registration                                          |
|**Goal**        | Registration of the anat on dwi                       |
|**Parameters**  | |
|**Time**        | N/A                                                   |
|**Output**      | - Anat (resample) <br> - 5tt (resampled, registered) <br> - norm (resampled, registered) <br> - mask (resampled, registered) <br> - aparc_aseg (resampled, registered) <br> - left, right ribbon (resampled, registered)|

#

## Goal

Registration task overlay anatomical and atlases on diffusion images. 

## Requirements

- Diffusion weighted images

## Parameters

If anatomical and diffusion images were acquired during the same acquisition session we use -usesqform -dof 6

## Implementation

### 1- Compute matrix  

```
function: freesurferToDWIMatrix = self.__freesurferToDWITransformation(b0, norm, extraArgs)
function: mrtrixMatrix = self.__transformFslToMrtrixMatrix(anat, b0, freesurferToDWIMatrix)
```

### 2- Resample

```
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

```
function: self.__applyRegistrationMrtrix(tt5, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(norm, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(mask, mrtrixMatrix)

function: self.__applyRegistrationMrtrix(aparcAsegFile, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(lhRibbon, mrtrixMatrix)
function: self.__applyRegistrationMrtrix(rhRibbon, mrtrixMatrix)

function: self.__applyRegistrationMrtrix(brodmann, mrtrixMatrix)

```

## Expected result(s) - Quality Assessment (QA)

[what should be produced by TOAD, the expected output]



# Preparation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Preparation                                           |
|**Goal**        | Create missing diffusion-weighted gradient scheme files <br> Check image's orientation|
|**Config file** | `stride_orientation` <br />`force_realign_strides`    |
|**Time**        | N/A                                                   |
|**Output**      | Re-oriented files <br> Missing gradients scheme files <br> Pictures for the QA (png and gif)|

#

## Goal

The preparation step ensures that all files required by TOAD are correctly provided.

## Minimal requirements

- Diffusion-weighted images (dwi)
- Anatomical image (anat)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Optimal requirements

- Diffusion-weigthed images (dwi)
- Anatomical image (anat)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Freesurfer folder
- Fieldmap (magnitude and phase) 
- Two b0s with opposite phase encoding directions (b0_ap, b0_pa)

## Config file parameters

[what are the options in the config file -- see parameters in the table]
#It is strongly suggest that the axes of your data should be order and directed in 1,2,3 layout
#If the images provides are in a different referential, we could flip them for the purpose of the pipeline
#stride_orientation should be 3 values comma separated
stride_orientation: 1,2,3
force_realign_strides: True

## Implementation

### 1- Produce missing diffusion-weighted gradient schemes (FSL, dipy and MRtrix compatibility)

```{.python}
function: __produceEncodingFiles(bEncs, bVecs, bVals, dwi)
```

### 2- Force re-orientation

```{.python}
function: __stride4DImage(dwi, bEncs, bVecs, bVals, expectedLayout)
function: mriutil.stride3DImage(image, self.buildName(image, "stride"), expectedLayout))
```

### 3- Check Freesurfer folder if exists

```{.python}
function: mriutil.isAfreesurferStructure(directory)
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weighted gradient schemes missing files will be created.  
- Every files provided will be re-oriented.  
- The preparation step will create an image (png) of the anatomic image and a gif from the dwi.  
- Finally, if b0_ap, b0_pa, magnitude or phase images exist, the preparation step will create an image (png) to be used in the QA

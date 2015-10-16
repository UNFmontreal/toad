# Preparation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Preparation                                           |
|**Goal**        | Create missing diffusion-weighted gradient scheme files <br> Check image's orientation|
|**Config file** | `stride_orientation` <br />`force_realign_strides`    |
|**Time**        | Few minutes                                           |
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

If `force_realign_strides` is set to `True`, the preparation task will require that the images provided be flipped so that they respect the `stride_orientation` option

- `force_realign_strides: True`
- `stride_orientation: 1,2,3`

**Warning**: It is strongly suggested that the axes of your data be ordered and directed in a 1,2,3 layout

## Implementation

### 1- Produce missing diffusion-weighted gradient schemes (FSL, dipy and MRtrix compatibility)

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/mrinfo" target="_blank">mrinfo</a> (diffusion-weighted gradient scheme)

### 2- Force re-orientation

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/mrconvert" target="_blank">mrconvert</a> (every images)

### 3- Check if the Freesurfer folder exists

```{.python}
function: mriutil.isAfreesurferStructure(directory)
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weighted gradient schemes missing files will be created.  
- Every files provided will be re-oriented.  
- The preparation step will create an image (png) of the anatomic image and a gif from the dwi.  
- Finally, if b0_ap, b0_pa, magnitude or phase images exist, the preparation step will create an image (png) to be used in the QA

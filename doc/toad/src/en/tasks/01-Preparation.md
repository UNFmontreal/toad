# Preparation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Preparation                                           |
|**Goal**        | Create missing diffusion-weighted gradient scheme files <br> Check image's orientation|
|**Parameters**  | Diffusion-weigthed and anatomical images <br> Diffusion-weighted gradient scheme files|
|**Time**        | N/A                                                   |
|**Output**      | Re-oriented files <br> Missing gradients scheme files <br> Pictures for the QA (png and gif)|

#

## Goal

Preparation step makes sure that every files needed for TOAD is provided.

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
- Two b0s with an opposite phase encoding direction (b0_ap, b0_pa)

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

- Diffusion-weighted gradient schemes missing files will be created.<br>
- Every files provided will be re-oriented.<br>
- The preparation step will create a png of the anatomic image and a gif from the dwi.<br>
- Finally, if b0_ap, b0_pa, magnitude or phase images exist preparation steps will create a png for the QA

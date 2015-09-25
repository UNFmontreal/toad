# Preparation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Preparation                                           |
|**Goal**        | Create missing gradient files <br> Check image's orientation|
|**Parameters**  | Diffusion and anatomical images <br> Gradient encoding file|
|**Time**        | N/A                                                   |
|**Output**      | Re-oriented files <br> Missing gradients files <br> Pictures for the QA (png and gif)|

#

## Goal

Preparation step makes sure that every files needed for TOAD is provided.

## Minimal requirements


- Diffusion images (dwi)
- Anatommical images (anat)
- Gradient vector (b or bvec and bval)

## Maximal requirements

- Diffusion images (dwi)
- Anatommical images (anat)
- Gradient vector (b, bvec and bval)
- Freesurfer folder
- Fieldmap (magnitude and phase) 
- Two b0 with an opposite phase encoding direction (b0_ap, b0_pa)

## Implementation

### 1- Produce encoding directions

```{.python}
function: __produceEncodingFiles(bEncs, bVecs, bVals, dwi)
```

### 2- Force re-orientation

```{.python}
function: __stride4DImage(dwi, bEncs, bVecs, bVals, expectedLayout)
function: mriutil.stride3DImage(image, self.buildName(image, "stride"), expectedLayout))
```

### 3- Check Freesurfer folder if exist

```{.python}
function: mriutil.isAfreesurferStructure(directory)
```

## Expected result(s) - Quality Assessment (QA)

- Gradient missing files will be created.<br>
- Every files provided will be re-oriented.<br>
- The preparation step will create a png of the anatomic image and a gif from the dwi.<br>
- Finally, if b0_ap, b0_pa, magnitude or phase images exist preparation steps will create a png for the QA

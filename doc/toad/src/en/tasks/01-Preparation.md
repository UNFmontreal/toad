# Preparation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Preparation                                           |
|**Goal**        | Create missing gradient files                         |
|                | Check image's orientation                             |
|**Parameters**  | Diffusion and anatomical images                       |
|                | Gradient encoding file                                |
|**Time**        | [Estimate processing time in a local machine]         |
|**Output**      | Re-oriented files                                     |
|                | Missing gradients files                               |
|                | Pictures for the QA  (png and gif)                    |

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
- Two b0 with an opposite phase encoding direction

## Implementation

### 1- Produce encoding directions

```
function: __produceEncodingFiles
```

### 2- Force re-orientation

```
function: __stride4DImage and mriutil.stride3DImage
```

### 3- Check Freesurfer folder if exist

```
function: mriutil.isAfreesurferStructure
```

## Expected result(s) - Quality Assessment (QA)

Gradient missing files will be created.
Every files provided will be re-oriented.
The preparation step will create a png of the anatomic image and a gif from the dwi.
Finally, if b0_ap, b0_pa, magnitude or phase images exist preparation steps will create a png for the QA

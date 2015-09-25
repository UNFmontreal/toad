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

```
[If only one step, do not add the subtitle step 1]
```

### 1- Produce encoding directions

```
[Tool or function used with the reference to the official documentation]
```

### 2- Force re-orientation

```
[Tool or function used with the reference to the official documentation]
```

### 3- Check Freesurfer folder if exist

```
[Tool or function used with the reference to the official documentation]
```

## Expected result(s) - Quality Assessment (QA)

Gradient missing files will be created.
Every files provided will be re-oriented.
The preparation step will create a png of the anatomic image and a gif from the dwi.
Finally, if b0_ap, b0_pa, magnitude or phase images exist preparation steps will create a png for the QA

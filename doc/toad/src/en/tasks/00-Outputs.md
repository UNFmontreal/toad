# Outputs
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | outputs                                    |
|**Goal**        | Copy every useful file                                    |
|**Time**        | Few seconds         |
|**Output**      | None                                     |

## Goal

The outputs step has been created to copy every file in the final version of the pipeline. Due to storage restrictions we won't copy them.

## Requirements

- Diffusion-weighted images (dwi) <br>
- Diffusion-weighted gradient scheme (b or bvec and bval) <br>
- Anatomical image resampled (anat)
- Mask image resampled
- Atlases image resampled
- Tensors and their metrics (fa, ad, rd, md)
- Constrained spherical deconvolution and their metrics (gfa, nufo)

## Implementation

### 1- Copy

```
function: util.copy(image, self.workingDir,  self.buildName(self.subject.getName(), postfix, 'nii.gz'))
function: self.__copyMetrics(['mrtrix', 'dipy', 'fsl'], ['fa','ad','rd','md'], 'tensor')
function: self.__copyMetrics(['mrtrix', 'dipy'], ['nufo','csd','gfa'], 'hardi')
```

## Expected result(s) - Quality Assessment (QA)

No QA page will be created since you have everything you need in the previous steps.



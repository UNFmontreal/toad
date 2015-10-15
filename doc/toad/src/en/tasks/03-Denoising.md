# Denoising
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Denoising                                             |
|**Goal**        | Apply a denoising algorithm on diffusion images (dwi) |
|**Parameters**  | dwi, gradient encoding directions, sigma <br> algorithm choice |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion images denoised                             |

## Goal

Denoising step denoises DWI depending on the algorithm choosen.

## Requirements

- Diffusion images (dwi)
- Gradient encoding direction (optional)

## Parameters

If NLMEANS algorithm is choosen we need to compute the sigma relative to diffusion images.


## Implementation

```
If denoising algorithm is set to None this step will be skipped
```

### 1- denoising algorithm: nlmeans

```
function: denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma)
```

### 2- denoising algorithm: lpca

```
function: self.get("algorithm") = "lpca"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

### 3- denoising algorithm: aonlm

```
function: self.get("algorithm") = "aonlm"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

## Expected result(s) - Quality Assessment (QA)

[what should be produced by TOAD, the expected output]

## References

[Coupe, P., Yger, P., Prima, S., Hellier, P., Kervrann, C., & Barillot, C. (2008). An optimized blockwise nonlocal means denoising filter for 3-D magnetic resonance images. *IEEE Transactions on Medical Imaging, 27*, 425–441. doi:10.1109/TMI.2007.906087](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=4359947)

[Manjón, J. V., Coupé, P., Concha, L., Buades, A., Collins, D. L., & Robles, M. (2013). Diffusion Weighted Image Denoising Using Overcomplete Local PCA. *PLoS ONE, 8(9)*, 1–12. doi:10.1371/journal.pone.0073021](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0073021)

[Manjón, J. V., Coupé, P., Martí-Bonmatí, L., Collins, D. L., & Robles, M. (2010). Adaptive non-local means denoising of MR images with spatially varying noise levels. *Journal of Magnetic Resonance Imaging, 31(1)*, 192–203. doi:10.1002/jmri.22003](http://onlinelibrary.wiley.com/doi/10.1002/jmri.22003/abstract)

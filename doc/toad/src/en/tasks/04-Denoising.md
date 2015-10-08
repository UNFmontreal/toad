# Denoising
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Denoising                                             |
|**Goal**        | Apply a denoising algorithm on Diffusion-weighted images |
|**Parameters**  | Diffusion-weighted images <br> Diffusion-weighted gradient scheme (b or bvec and bval) <br> Sigma <br> Algorithm choice |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weighted images denoised                             |

## Goal

Denoising step denoises diffusion-weighted images (DWI) depending on the algorithm choosen.

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Parameters

If NLMEANS algorithm is choosen we need to compute the sigma relative to diffusion images using piesno algorithm.
For 32 coils channel acquisition from UNF we compute the standard deviation of the noise in DWI as sigma.

## Implementation

If denoising algorithm is set to None this step will be skipped


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

- Diffusion-weigthed images corrected
- A gif before/after to see the differences in DWI

## References

Coupe, P., Yger, P., Prima, S., Hellier, P., Kervrann, C., & Barillot, C. (2008). An Optimized Blockwise Nonlocal Means Denoising Filter for 3-D Magnetic Resonance Images. *IEEE Transactions on Medical Imaging, 27(4), 425-441*. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2881565&tool=pmcentrez&rendertype=abstract

Manjón, J. V., Coupé, P., Concha, L., Buades, A., Collins, D. L., & Robles, M. (2013). Diffusion weighted image denoising using overcomplete local PCA. *PloS one, 8(9), e73021*. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=3760829&tool=pmcentrez&rendertype=abstract

Manjón, J. V., Coupé, P., Martí-Bonmatí, L., Collins, D. L., & Robles, M. (2010). Adaptive non-local means denoising of MR images with spatially varying noise levels. *Journal of magnetic resonance imaging : JMRI, 31(1), 192-203*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/20027588

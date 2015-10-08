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

[Coupe2008]	P. Coupe, P. Yger, S. Prima, P. Hellier, C. Kervrann, C. Barillot, “An Optimized Blockwise Non Local Means Denoising Filter for 3D Magnetic Resonance Images”, IEEE Transactions on Medical Imaging, 27(4):425-441, 2008.

J. V. Manjon, P. Coupé, L. Concha, A. Buades, D. L. Collins, M. Robles. Diffusion Weighted Image Denoising using overcomplete Local PCA. PLoS ONE 8(9): e73021. doi:10.1371/journal.pone.0073021. 

José Manjón, Pierrick Coupé, Luis Martí-Bonmatí, D Louis Collins, Montserrat Robles. Adaptive non-local means denoising of MR images with spatially varying noise levels.. Journal of Magnetic Resonance Imaging, Wiley-Blackwell, 2010, 31 (1), pp.192-203.

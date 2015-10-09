# Denoising
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Denoising                                             |
|**Goal**        | Apply a denoising algorithm on diffusion-weighted images |
|**Config file** | `algorithm` <br />`rician`<br />`number_array_coil`<br />`cleanup`<br />`ignore`                                      |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weighted images denoised                    |

## Goal

Denoising step denoises diffusion-weighted images (DWI) depending on the algorithm choosen.

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Config file parameters

Algorithm chosen for denoising the dwi {lpca, aonlm, nlmeans}
- `algorithm: nlmeans`

Noise model, { 1 for rician noise model and 0 for gaussian noise model}
- `rician: 1`

`number_array_coil`: The number of phase array coils of the MRI scanner.
If your scanner does a SENSE reconstruction, ALWAYS use `number_array_coil=1`, as the noise profile is always Rician.
If your scanner does a GRAPPA reconstruction, set `number_array_coil` as the number of phase array coils.
- `number_array_coil: 1`

remove extra files at the end of the tasks
- `cleanup: False`

Ignore denoising task: **not recommended**
- `ignore: False`

## Implementation

If denoising algorithm is set to None this step will be skipped


### 1- denoising algorithm: nlmeans

- [nlmeans](http://nipy.org/dipy/examples_built/denoise_nlmeans.html#example-denoise-nlmeans)

### 2- denoising algorithm: lpca

```{.python}
function: self.get("algorithm") = "lpca"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

### 3- denoising algorithm: aonlm

```{.python}
function: self.get("algorithm") = "aonlm"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weigthed images corrected
- A gif showing the DWI data before and after correction

## References

- Denoising: nlmeans <br>
> Coupe, P., Yger, P., Prima, S., Hellier, P., Kervrann, C., & Barillot, C. (2008). An Optimized Blockwise Nonlocal Means Denoising Filter for 3-D Magnetic Resonance Images. *IEEE Transactions on Medical Imaging, 27(4), 425-441*. [[Link to the article](http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2881565&tool=pmcentrez&rendertype=abstract)]

- Denoising: lpca <br>
> Manjón, J. V., Coupé, P., Concha, L., Buades, A., Collins, D. L., & Robles, M. (2013). Diffusion weighted image denoising using overcomplete local PCA. *PloS one, 8(9), e73021*. [[Link to the article](http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=3760829&tool=pmcentrez&rendertype=abstract)]

- Denoising: aonlm <br>
> Manjón, J. V., Coupé, P., Martí-Bonmatí, L., Collins, D. L., & Robles, M. (2010). Adaptive non-local means denoising of MR images with spatially varying noise levels. *Journal of magnetic resonance imaging : JMRI, 31(1), 192-203*. [[Link to the article](http://www.ncbi.nlm.nih.gov/pubmed/20027588)]

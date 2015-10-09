# Denoising
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Denoising                                             |
|**Goal**        | Apply a denoising algorithm on diffusion-weighted images |
|**Config file** | `algorithm` <br />`script_name`<br />`matlab_script`<br />`rician`<br />`cleanup`<br />`ignore`<br />`number_array_coil`                                      |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weighted images denoised                    |

## Goal

Denoising step denoises diffusion-weighted images (DWI) depending on the algorithm choosen.

## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)

## Config file parameters

[what are the options in the config file -- see parameters in the table]
#algorithm chosen for denoising the dwi {lpca, aonlm, nlmeans}
algorithm: nlmeans

#matlab script filename with .m extension omit: not for nlmeans
script_name: denoise

#matlab script filename with .m extension omit: not for nlmeans
matlab_script: pyscript

# undocumented: not for nlmeans
beta: 1

#noise model, { 1 for rician noise model and 0 for gaussian noise model}
rician: 1

#remove extra files at the end of the tasks
cleanup: False

#ignore denoising task: not recommended
ignore: False

#N: The number of phase array coils of the MRI scanner.
#If your scanner does a SENSE reconstruction, ALWAYS use number_array_coil=1, as the noise
#profile is always Rician.
#If your scanner does a GRAPPA reconstruction, set number_array_coil as the number
#of phase array coils.
number_array_coil: 32

#file name containing sigma values
sigma_filename: sigma_values.dat


If NLMEANS algorithm is choosen we need to compute the sigma relative to diffusion images using piesno algorithm.
For 32 coils channel acquisition from UNF we compute the standard deviation of the noise in DWI as sigma.


## Implementation

If denoising algorithm is set to None this step will be skipped


### 1- denoising algorithm: nlmeans

```R
function: denoisingData = dipy.denoise.nlmeans.nlmeans(dwiData, sigma)
```

### 2- denoising algorithm: lpca

```R
function: self.get("algorithm") = "lpca"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

### 3- denoising algorithm: aonlm

```R
function: self.get("algorithm") = "aonlm"
function: scriptName = self.__createMatlabScript(dwiUncompress, tmp)
function: self.__launchMatlabExecution(scriptName)
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weigthed images corrected
- A gif showing the DWI data before and after correction

## References

- Denoising: nlmeans <br>
> Coupe, P., Yger, P., Prima, S., Hellier, P., Kervrann, C., & Barillot, C. (2008). An Optimized Blockwise Nonlocal Means Denoising Filter for 3-D Magnetic Resonance Images. *IEEE Transactions on Medical Imaging, 27(4), 425-441*. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2881565&tool=pmcentrez&rendertype=abstract

- Denoising: lpca <br>
> Manjón, J. V., Coupé, P., Concha, L., Buades, A., Collins, D. L., & Robles, M. (2013). Diffusion weighted image denoising using overcomplete local PCA. *PloS one, 8(9), e73021*. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=3760829&tool=pmcentrez&rendertype=abstract

- Denoising: aonlm <br>
> Manjón, J. V., Coupé, P., Martí-Bonmatí, L., Collins, D. L., & Robles, M. (2010). Adaptive non-local means denoising of MR images with spatially varying noise levels. *Journal of magnetic resonance imaging : JMRI, 31(1), 192-203*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/20027588

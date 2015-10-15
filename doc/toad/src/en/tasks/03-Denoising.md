# Denoising
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Denoising                                             |
|**Goal**        | Apply a denoising algorithm on diffusion-weighted images |
|**Config file** | `algorithm` <br />`rician`<br />`number_array_coil`<br />`cleanup`<br />`ignore`                                      |
|**Time**        | Depends on the denoising algorithm                                                 |
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

- <a href="http://nipy.org/dipy/examples_built/denoise_nlmeans.html#example-denoise-nlmeans" target="_blank">nlmeans</a>

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


### Articles


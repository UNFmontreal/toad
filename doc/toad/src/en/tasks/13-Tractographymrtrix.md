# Tractographymrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractographyhmrtrix                                    |
|**Goal**        | Run tractography on tensors and constrained spherical deconvolution using tckgen from MRtrix                                   |
|**Parameters**  | - Diffusion-weigthed images (dwi) <br> - Diffusion-weighted gradient scheme (b or bvec and bval) <br> - Constrained spherical deconvolution (csd) <br> - 5tt map|
|**Time**        | N/A         |
|**Output**      | - Probabilist tensor tractography and connectome <br> - Probabilist tensor tractography and connectome <br> - Probabilist "sifted" csd tractography and connectome |

## Goal

Tractographymrtrix step run tractography on different reconstruction method (tensor, csd). It creates as well connectome from anatomical segmentation.


## Requirements

- Diffusion-weigthed images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Constrained spherical deconvolution (csd)
- Five-tissue-type maps (5tt)
- Atlas (brodmann, aal2) optional

## Parameters

We use default paramaters suggested in MRtrix documentation.


## Implementation

### 1- Tractographies from diffusion tensor (dt)

Determinist tractography 
```{.python}
function: tckDet = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_det', 'tck'), mask, tt5, seed_gmwmi, bFile, 'Tensor_Det')
```

Probabilist tractography 

```{.python}
function: tckProb = self.__tckgenTensor(dwi, self.buildName(dwi, 'tensor_prob', 'tck'), mask, tt5, seed_gmwmi, bFile, 'Tensor_Prob')
```

### 2- Tractographies from constrained spherical deconvolution

Probabilist tractography 
```{.python}
function: hardiTck = self.__tckgenHardi(csd, self.buildName(csd, 'hardi_prob', 'tck'), tt5)
```

### 3- Spherical-deconvolution informed filtering of tractograms (SIFT)

```{.python}
function: tcksift = self.__tcksift(hardiTck, csd)
```

### 4- Creation of the structural connectome

```{.python}
function: tcksiftConnectome = self.__tck2connectome(tcksift, brodmann, self.buildName(tcksift, 'connectome', 'csv'))
```

## Expected result(s) - Quality Assessment (QA)

Tractographymrtrix runs determinist tractographies from
- Tensor reconstruction

Tractographymrtrix runs probabilist tractographies from
- Tensor reconstruction
- Constrained spherical deconvolution

It filters tractograms using SIFT algorithm
It creates structural connectomes from tractographies

It creates PNG from a dummy examples for the QA so we can check the results 
It creates PNG of the structural connectomes.

## References

- Tractography 

Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2012). Anatomically-constrained tractography: improved diffusion MRI streamlines tractography through effective use of anatomical information. *NeuroImage, 62(3), 1924-38*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/22705374

- SIFT

Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2013). SIFT: Spherical-deconvolution informed filtering of tractograms. *NeuroImage, 67, 298-312*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/23238430

Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2015). The effects of SIFT on the reproducibility and biological accuracy of the structural connectome. *NeuroImage, 104, 253-65*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/25312774

Calamante, F., Smith, R. E., Tournier, J.-D., Raffelt, D., & Connelly, A. (2015). Quantification of voxel-wise total fibre density: Investigating the problems associated with track-count mapping. *NeuroImage, 117, 284-93*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/26037054

## Highly recommanded readings

- References
- MRtrix wiki<br>
-- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tckgen" target="_blank">MRtrix tckgen</a> <br>
-- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tcksift" target="_blank">MRtrix tcksift</a> <br>
-- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tck2connectome" target="_blank">MRtrix tck2connectome</a> <br>

- MRtrix workflows<br>
-- <a href="https://github.com/MRtrix3/mrtrix3/wiki/Anatomically-Constrained-Tractography-(ACT)" target="_blank">Anatomical constrained tractography</a> <br>
-- <a href="https://github.com/MRtrix3/mrtrix3/wiki/SIFT" target="_blank">SIFT</a> <br>

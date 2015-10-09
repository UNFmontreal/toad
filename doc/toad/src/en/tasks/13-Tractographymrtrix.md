# Tractographymrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractographyhmrtrix                                    |
|**Goal**        | Run tractography on tensors and constrained spherical deconvolution using tckgen from MRtrix                                   |
|**Parameters**  | `step` <br> `maxlength` <br> `number_tracks` <br> `downsample` <br> `ignore`|
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

## Config files parameter

We use default paramaters suggested in MRtrix documentation.

Step size of the algorithm in mm (default is 0.1 x voxelsize; for iFOD2: 0.5 x voxelsize).
- `step: 0.2`

Maximum length of any track in mm
- `maxlength: 300`

Desired number of tracks
- `number_tracks: 1000000`

Downsample factor to reduce output file size
- `downsample: 8`

Ignore tractographymrtrix task: not recommended <br>
- `ignore: False`

## Implementation

### 1- Tractographies 

[tckgen](https://github.com/MRtrix3/mrtrix3/wiki/tckgen)

### 2- Spherical-deconvolution informed filtering of tractograms (SIFT)

[tcksift](https://github.com/MRtrix3/mrtrix3/wiki/sift)

### 3- Creation of the structural connectome

[tck2connectome](https://github.com/MRtrix3/mrtrix3/wiki/tck2connectome)

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


### Scientific articles 
- Tractography 

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2012). Anatomically-constrained tractography: improved diffusion MRI streamlines tractography through effective use of anatomical information. *NeuroImage, 62(3), 1924-38*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/22705374

- SIFT

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2013). SIFT: Spherical-deconvolution informed filtering of tractograms. *NeuroImage, 67, 298-312*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/23238430

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2015). The effects of SIFT on the reproducibility and biological accuracy of the structural connectome. *NeuroImage, 104, 253-65*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/25312774

> Calamante, F., Smith, R. E., Tournier, J.-D., Raffelt, D., & Connelly, A. (2015). Quantification of voxel-wise total fibre density: Investigating the problems associated with track-count mapping. *NeuroImage, 117, 284-93*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/26037054

### Associated documentation

- [MRtrix tckgen](https://github.com/MRtrix3/mrtrix3/wiki/tcksift)
- [MRtrix tcksift](https://github.com/MRtrix3/mrtrix3/wiki/tcksift)
- [MRtrix tck2connectome](https://github.com/MRtrix3/mrtrix3/wiki/tck2connectome)
- [MRtrix workflow ACT](https://github.com/MRtrix3/mrtrix3/wiki/Anatomically-Constrained-Tractography-(ACT))
- [MRtrix workflow SIFT](https://github.com/MRtrix3/mrtrix3/wiki/SIFT)

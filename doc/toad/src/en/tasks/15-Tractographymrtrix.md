# Tractographymrtrix
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | tractographymrtrix                                    |
|**Goal**        | Run tractography on tensors and constrained spherical deconvolution using tckgen from MRtrix |
|**Config file** | `step` <br> `maxlength` <br> `number_tracks` <br> `downsample` <br> `ignore`|
|**Time**        | About 2 hours                                         |
|**Output**      | - Probabilistic tensor tractography and connectome <br> - Probabilistic tensor tractography and connectome <br> - Probabilistic "sifted" csd tractography and connectome |

#

## Goal

The tractographymrtrix step computes tractography using different reconstruction methods (tensor, csd). 
It also creates connectomes from anatomical segmentations.


## Requirements

- Diffusion-weighted images (dwi)
- Diffusion-weighted gradient scheme (b or bvec and bval)
- Constrained spherical deconvolution (csd)
- Five-tissue-type maps (5tt)
- Atlas (brodmann, aal2) optional

## Config files parameter

We use default paramaters suggested in the MRtrix documentation.

Step size of the algorithm in mm (default is 0.1 x voxelsize; for iFOD2: 0.5 x voxelsize).

- `step: 0.2`

Maximum length of any track in mm

- `maxlength: 300`

Desired number of tracks

- `number_tracks: 1000000`

Downsample factor to reduce output file size

- `downsample: 8`

Ignore tractographymrtrix task: not recommended

- `ignore: False`

## Implementation

### 1- Tractographies 

<a href="https://github.com/MRtrix3/mrtrix3/wiki/tckgen" target="_blank">MRtrix tckgen</a>

### 2- Spherical-deconvolution informed filtering of tractograms (SIFT)

<a href="https://github.com/MRtrix3/mrtrix3/wiki/sift" target="_blank">MRtrix tcksift</a>

### 3- Creation of the structural connectome

<a href="https://github.com/MRtrix3/mrtrix3/wiki/tck2connectome" target="_blank">MRtrix tck2connectome</a>

## Expected result(s) - Quality Assessment (QA)

Tractographymrtrix runs deterministic tractographies from

- Tensor reconstruction

Tractographymrtrix runs probabilistic tractographies from

- Tensor reconstruction
- Constrained spherical deconvolution

It filters tractograms using the SIFT algorithm.  
It creates structural connectomes from tractographies.

Production of an image (png) from a dummy example for the QA in order to check the results.   
Production of an image (png) of the structural connectomes.

## References

### Associated documentation

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tcksift" target="_blank">MRtrix tckgen</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tcksift" target="_blank">MRtrix tcksift</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/tck2connectome" target="_blank">MRtrix tck2connectome</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/Anatomically-Constrained-Tractography-(ACT)" target="_blank">MRtrix workflow ACT</a>
- <a href="https://github.com/MRtrix3/mrtrix3/wiki/SIFT" target="_blank">MRtrix workflow SIFT</a>

### Articles 

- Tractography 

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2012). Anatomically-constrained tractography: improved diffusion MRI streamlines tractography through effective use of anatomical information. *NeuroImage, 62(3)*, 1924-1938. [<a href="XXXXXXXX" target="_blank">Link to the article</a>]Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/22705374

- SIFT

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2013). SIFT: Spherical-deconvolution informed filtering of tractograms. *NeuroImage, 67*, 298-312. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/23238430" target="_blank">Link to the article</a>]

> Smith, R. E., Tournier, J.-D., Calamante, F., & Connelly, A. (2015). The effects of SIFT on the reproducibility and biological accuracy of the structural connectome. *NeuroImage, 104*, 253-265. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/25312774" target="_blank">Link to the article</a>] 

> Calamante, F., Smith, R. E., Tournier, J.-D., Raffelt, D., & Connelly, A. (2015). Quantification of voxel-wise total fibre density: Investigating the problems associated with track-count mapping. *NeuroImage, 117*, 284-293. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/26037054" target="_blank">Link to the article</a>] 


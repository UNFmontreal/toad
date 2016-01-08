# Atlas Registration
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Atlas Registration                                          |
|**Goal**        | Registration of atlases on diffusion-weighted images |
|**Config file** | `cleanup`                                             |
|**Time**        | Few minutes                                           |
|**Output**      | - AAL2 atlas (resampled, registered) <br> - 7networks (resampled, registered)|

#

## Goal

The registration step overlays atlases on the diffusion-weighted images. 

## Requirements

- Registration matrix (registration step)
- 7networks atlas
- AAL2 atlas

## Config file parameters

If anatomical and diffusion-weighted images were acquired during the same acquisition session we use -usesqform -dof 6 <br>

Remove extra files

- `cleanup: False`

## Implementation

### 1- Resample

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/flirt" target="_blank">FSL flirt</a>

### 2- Registration

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/mrtransform" target="_blank">MRtrix mrtransform</a>

## Expected result(s) - Quality Assessment (QA)

- Production of an image (png) of atlases overlayed on brain mask.

## References

### Articles

- Jenkinson, M., Bannister, P., Brady, M., & Smith, S. (2002). Improved optimization for the robust and accurate linear registration and motion correction of brain images. *NeuroImage, 17(2), 825-841*. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/12377157" target="_blank">Link to the article</a>]

- Jenkinson, M., & Smith, S. (2001). A global optimisation method for robust affine registration of brain images. *Medical Image Analysis, 5(2), 143-156*. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/11516708" target="_blank">Link to the article</a>]

- Greve, D. N., & Fischl, B. (2009). Accurate and robust brain image alignment using boundary-based registration. *NeuroImage, 48(1), 63-72*. [<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2733527&tool=pmcentrez&rendertype=abstract" target="_blank">Link to the article</a>]


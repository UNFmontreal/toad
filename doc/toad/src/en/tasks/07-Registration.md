# Registration
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Registration                                          |
|**Goal**        | Registration of the anatomical to diffusion-weighted images |
|**Config file** | `cleanup`                                             |
|**Time**        | Few minutes                                           |
|**Output**      | - Anatomical images (resample) <br> - 5tt (resampled, registered) <br> - norm (resampled, registered) <br> - mask (resampled, registered) <br> - aparc_aseg (resampled, registered) <br> - left, right ribbon (resampled, registered)|

#

## Goal

The registration step overlays the anatomical image on the diffusion-weighted images. 

## Requirements

- Diffusion-weighted images (dwi)
- Anatomical image (anat)
- 5tt, norm, mask, aparc_aseg and left right ribbon from parcellation step (Freesurfer pipeline) 

## Config file parameters

If anatomical and diffusion-weighted images were acquired during the same acquisition session we use -usesqform -dof 6 <br>

Remove extra files

- `cleanup: False`

## Implementation

### 1- Compute matrix  

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/flirt" target="_blank">FSL flirt</a>

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/transformcalc" target="_blank">MRtrix transformcalc</a>

### 2- Resample

- <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/flirt" target="_blank">FSL flirt</a>

### 3- Registration

- <a href="https://github.com/MRtrix3/mrtrix3/wiki/mrtransform" target="_blank">MRtrix mrtransform</a>


## Expected result(s) - Quality Assessment (QA)

- Production of an image (png) of the B0 overlayed on brain mask and its boundaries
- Production of an image (png) of the B0 overlayed on aparc_aseg file and within the boundaries of the brain mask

## References

### Articles

- Jenkinson, M., Bannister, P., Brady, M., & Smith, S. (2002). Improved optimization for the robust and accurate linear registration and motion correction of brain images. *NeuroImage, 17(2), 825-841*. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/12377157" target="_blank">Link to the article</a>]

- Jenkinson, M., & Smith, S. (2001). A global optimisation method for robust affine registration of brain images. *Medical Image Analysis, 5(2), 143-156*. [<a href="http://www.ncbi.nlm.nih.gov/pubmed/11516708" target="_blank">Link to the article</a>]

- Greve, D. N., & Fischl, B. (2009). Accurate and robust brain image alignment using boundary-based registration. *NeuroImage, 48(1), 63-72*. [<a href="http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2733527&tool=pmcentrez&rendertype=abstract" target="_blank">Link to the article</a>]


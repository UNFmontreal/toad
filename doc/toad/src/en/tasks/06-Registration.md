# Registration
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Registration                                          |
|**Goal**        | Registration of the anatomical on diffusion-weighted images |
|**Config file** | `cleanup`                                             |
|**Time**        | N/A                                                   |
|**Output**      | - Anatomical images (resample) <br> - 5tt (resampled, registered) <br> - norm (resampled, registered) <br> - mask (resampled, registered) <br> - aparc_aseg (resampled, registered) <br> - left, right ribbon (resampled, registered)|

#

## Goal

The registration step overlays the anatomical image and atlases on the diffusion-weigthed images. 

## Requirements

- Diffusion-weigthed images (dwi)
- Anatomical image (anat)
- 5tt, norm, mask, aparc_aseg and left right ribbon from parcellation step (Freesurfer pipeline) 

## Config file parameters

If anatomical and diffusion-weigthed images were acquired during the same acquisition session we use -usesqform -dof 6 <br>

Remove extra files
- `cleanup: False`

## Implementation

### 1- Compute matrix  

- [flirt](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/flirt)

- [transformcalc](https://github.com/MRtrix3/mrtrix3/wiki/transformcalc)


### 2- Resample


- [flirt](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/flirt)

### 3- Registration

- [mrtransform](https://github.com/MRtrix3/mrtrix3/wiki/mrtransform)

## Expected result(s) - Quality Assessment (QA)

- Produce an image (png) of the B0 overlayed by brain mask and its boundaries
- Produce an image (png) of the B0 overlayed by aparc_aseg file and by the boundaries of the brain mask

## References

### Scientific articles

Jenkinson, M., Bannister, P., Brady, M., & Smith, S. (2002). Improved optimization for the robust and accurate linear registration and motion correction of brain images. *NeuroImage, 17(2), 825-41*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/12377157

Jenkinson, M., & Smith, S. (2001). A global optimisation method for robust affine registration of brain images. *Medical image analysis, 5(2), 143-56*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/11516708

Greve, D. N., & Fischl, B. (2009). Accurate and robust brain image alignment using boundary-based registration. *NeuroImage, 48(1), 63-72*. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=2733527&tool=pmcentrez&rendertype=abstract


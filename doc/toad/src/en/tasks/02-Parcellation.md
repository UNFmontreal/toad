# Parcellation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Parcellation                                          |
|**Goal**        | Run Freesurfer pipeline                               |
|**Config file** | `intrasubject` <br />`directive`<br />`cleanup` |
|**Time**        | N/A                                                   |
|**Output**      | - Anatomical from Freesurfer <br> - Aparc_aseg segmentation <br> - Mask from aparc_aseg file <br> - lh_ribbon and rh_ribbon <br> - 5tt image (five-tissue-type)|

#

## Goal

The parcellation step creates the required masks using Freesurfer functions.

## Requirements

- Anatomical image (anat)

## Config file parameters

Specify if the anatomical and dwi where acquire during the same session<br />
- `intrasubject: True`<br />

Option available for Freesurfer recon-all command {all,autorecon-all,autorecon1,autorecon2,autorecon2-cp,autorecon2-wm,autorecon2-inflate1,autorecon2-perhemi,autorecon3 }<br />
- `directive: all`<br />

Remove extra files<br />
- `cleanup: True`<br />

## Implementation

### 1- Run reconAll from Freesurfer [ref: [freesurferwiki](#wikiFS)]

- [recon-all](https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all) (on anat)

### 2- Conversion

- [mrconvert](https://github.com/MRtrix3/mrtrix3/wiki/mrconvert) (all needed files from freesurfer)

### 3- Creation of masks from Freesurfer atlases

```{.python}
function: self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))
function: self.__create5ttImage()
```

- [mri_vol2vol]()

### 4- Re-orientation

- [mrconvert](https://github.com/MRtrix3/mrtrix3/wiki/mrconvert) (all needed files from freesurfer)

## Expected result(s) - Quality Assessment (QA)

- Anatomical, norm, rh_ribbon and lh_ribbon mgz images will be converted into nifti format from Freesurfer pipeline.
- Brodmann, Choi and Buckner atlases will be created.
- A mask of the brain will be computed using aparc_aseg.
- 5tt map will be computed using lh.white, rh.white, lh.pial and rh.pial from Freesurfer.

## References

### Associated documentation

- <a name="wikiFS"></a>[FreeSurfer Wiki](http://freesurfer.net/fswiki)

### Articles

Dale, A. M., Fischl, B., & Sereno, M. I. (1999). Cortical surface-based analysis. I. Segmentation and surface reconstruction. *NeuroImage, 9(2), 179-94*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/9931268

Collins, D. L., Neelin, P., Peters, T. M., & Evans, A. C.Automatic 3D intersubject registration of MR volumetric data in standardized Talairach space. *Journal of computer assisted tomography*.

Fischl, B., Sereno, M. I., & Dale, A. M. (1999). Cortical surface-based analysis. II: Inflation, flattening, and a surface-based coordinate system. *NeuroImage, 9(2), 195-207*. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/9931269

Fischl, B., Sereno, M. I., Tootell, R. B., & Dale, A. M. (1999). High-resolution intersubject averaging and a coordinate system for the cortical surface. Human brain mapping, 8(4), 272-84. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/10619420

Fischl, B., & Dale, A. M. (2000). Measuring the thickness of the human cerebral cortex from magnetic resonance images. Proceedings of the National Academy of Sciences of the United States of America, 97(20), 11050-5. Retrieved from http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=27146&tool=pmcentrez&rendertype=abstract

Fischl, B., Salat, D. H., Busa, E., Albert, M., Dieterich, M., Haselgrove, C., Kouwe, A. van der, et al. (2002). Whole brain segmentation: automated labeling of neuroanatomical structures in the human brain. Neuron, 33(3), 341-55. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/11832223

Fischl, B., Kouwe, A. van der, Destrieux, C., Halgren, E., Ségonne, F., Salat, D. H., Busa, E., et al. (2004). Automatically parcellating the human cerebral cortex. Cerebral cortex (New York, N.Y. : 1991), 14(1), 11-22. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/14654453


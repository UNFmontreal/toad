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

- [mri_vol2vol]

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

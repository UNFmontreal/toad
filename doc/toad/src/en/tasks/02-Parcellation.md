# Parcellation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Parcellation                                          |
|**Goal**        | Run Freesurfer pipeline                               |
|**Config file** | `intrasubject` <br />`freesurfer_anat`<br />`aparc_aseg`<br />`rh_ribbon` & `lh_ribbon`<br /> `brodmann`<br />`buckner`<br />`tt5`</br />`choi`<br />`norm`<br />`mask`<br />`directive`<br />`id`<br />`template_brodmann` <br />`template_buckner`<br />`template_choi`<br />`cleanup` |
|**Time**        | N/A                                                   |
|**Output**      | - Anatomical from Freesurfer <br> - Aparc_aseg segmentation <br> - Mask from aparc_aseg file <br> - lh_ribbon and rh_ribbon <br> - 5tt image (five-tissue-type)|

#

## Goal

The parcellation step creates the required masks using Freesurfer functions.

## Requirements

- Anatomical image (anat)

## Config file parameters

[what are the options in the config file -- see parameters in the table]

#specify if the anatomical and dwi where acquire during the same session
intrasubject: True

#name of the expected output white matter image
freesurfer_anat = freesurfer_anat.nii.gz

#name of the expected output parcellation image
aparc_aseg = aparc_aseg.nii.gz

#name of the expected output ribbon image
rh_ribbon = rh_ribbon.nii.gz
lh_ribbon = lh_ribbon.nii.gz

#name of the expected brodmann area image
brodmann = brodmann.nii.gz

#name of the expected buckner area image
buckner = buckner.nii.gz

#name of the expected 5tt area image
tt5 = 5tt.nii.gz

#name of the expected choi area image
choi = choi.nii.gz

#name of the norm image
norm = norm.nii.gz

#name of the brain mask image
mask = brain_mask.nii.gz

#Directive to pass to freesurfer {all,autorecon-all,autorecon1,autorecon2,autorecon2-cp,autorecon2-wm,autorecon2-inflate1,autorecon2-perhemi,autorecon3 }
directive: all

#name of the subdirecory that will be created
id: freesurfer

#subdirectory where to find brodmann normalize templates
template_brodmann: brodmann.nii.gz

#subdirectory where to find buckner normalize templates
template_buckner: Buckner2011_7Networks_MNI152_FreeSurferConformed1mm_TightMask.nii.gz

#subdirectory where to find choi normalize templates
template_choi: Choi2012_7Networks_MNI152_FreeSurferConformed1mm_TightMask.nii.gz

#remove extra files
cleanup: True

## Implementation

### 1- Run reconAll from Freesurfer [ref: [freesurferwiki](#wikiFS)]

```{.python}
function: self.__submitReconAll(anat)
```

### 2- Conversion

```{.python}
function: self.__convertFeesurferImageIntoNifti(anat)
```

### 3- Creation of masks from Freesurfer atlases

```{.python}
function: self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))
function: self.__createImageFromAtlas("template_buckner", self.get("buckner"))
function: self.__createImageFromAtlas("template_brodmann", self.get("brodmann"))
function: self.__createImageFromAtlas("template_choi", self.get("choi"))
function: self.__create5ttImage()
```

### 4- Re-orientation

```{.python}
function: self.__convertAndRestride(self.__findImageInDirectory(source, os.path.join(self.workingDir, self.id)), target)
```

## Expected result(s) - Quality Assessment (QA)

- Anatomical, norm, rh_ribbon and lh_ribbon mgz images will be converted into nifti format from Freesurfer pipeline.
- Brodmann, Choi and Buckner atlases will be created.
- A mask of the brain will be computed using aparc_aseg.
- 5tt map will be computed using lh.white, rh.white, lh.pial and rh.pial from Freesurfer.

## References

### Websites

- <a name="wikiFS"></a>[FreeSurfer Wiki](http://freesurfer.net/fswiki)

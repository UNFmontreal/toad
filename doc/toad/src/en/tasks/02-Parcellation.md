# Parcellation
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Parcellation                                          |
|**Goal**        | Run Freesurfer pipeline                                |
|**Parameters**  | anat image                                            |
|**Time**        | N/A                                                   |
|**Output**      | - anat from Freesurfer <br> - Aparc_aseg segmentation <br> - Mask from aparc_aseg file <br> - lh_ribbon and rh_ribbon <br> - 5tt image (five-tissue-type)|

#

## Goal

Parcellation step create from Freesurfer pipeline different masks.

## Requirements

anat image

## Implementation

### 1- Run reconAll from Freesurfer [Ref](http://freesurfer.net/fswiki)

```{.python}
function self.__submitReconAll(anat)
```

### 2- Conversion

```{.python}
function self.__convertFeesurferImageIntoNifti(anat)
```

### 3- Creation of masks from Freesurfer atlases

```{.python}
function self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))
function self.__createImageFromAtlas("template_buckner", self.get("buckner"))
function self.__createImageFromAtlas("template_brodmann", self.get("brodmann"))
function self.__createImageFromAtlas("template_choi", self.get("choi"))
function self.__create5ttImage()
```

### 4- Re-orientation

```{.python}
function self.__convertAndRestride(self.__findImageInDirectory(source, os.path.join(self.workingDir, self.id)), target)
```

## Expected result(s) - Quality Assessment (QA)

- anat, norm, rh_ribbon and lh_ribbon mgz images will be converted into nifti format from Freesurfer pipeline.
- Brodmann, Choi and Buckner atlases will be created.
- A mask of the brain will be computed using aparc_aseg.
- 5tt map will be computed using lh.white, rh.white, lh.pial and rh.pial from Freesurfer.



# Masking
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Masking                                               |
|**Goal**        | Creation of masks from atlases                        |
|**Time**        | Few minutes                                           |
|**Output**      | - Seed grey/white matter interface <br> - White matter mask <br> - Mask from aparc_aseg (253 and 1024) |

#

## Goal

The masking step creates the masks from aparc_aseg and 5tt maps

## Requirements

- Mask (resampled, registered)
- Aparc_Aseg (resampled, registered)
- 5tt mask (resampled, registered)

## Implementation

### 1- Creation of specific masks for tractography

```{.python}
function: seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)
seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)
whiteMatterAct = self.__extractWhiteMatterFrom5tt(tt5Resample)
```

### 2- Creation of specific masks using apar_aseg

```{.python}
self.info(mriutil.mrcalc(aparcAsegResample, '253', self.buildName('aparc_aseg', ['253', 'mask'], 'nii.gz')))
self.info(mriutil.mrcalc(aparcAsegResample, '1024', self.buildName('aparc_aseg', ['1024', 'mask'],'nii.gz')))
```

## Expected result(s) - Quality Assessment (QA)

- Production of a white matter image (png)

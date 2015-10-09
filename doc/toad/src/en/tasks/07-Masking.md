# Masking
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Masking                                               |
|**Goal**        | Creation of masks from atlases                        |
|**Config file** | `act_extract_at_axis` <br />`act_extract_at_coordinate`<br />`start_seeds` & `stop_seeds`<br />`exclude_seeds`    |
|**Time**        | N/A         |
|**Output**      | - Seed grey/white matter interface <br> - White matter mask <br> - Mask from aparc_aseg (253 and 1024) |

#

## Goal

The masking step creates the masks from aparc_aseg and 5tt maps

## Requirements

- Mask (resampled, registered)
- Aparc_Aseg (resampled, registered)
- 5tt mask (resampled, registered)

## Config file parameters

[what are the options in the config file -- see parameters in the table]

#extract the white matter mask from the act
act_extract_at_axis: 3

#extract the white matter mask from the act
act_extract_at_coordinate: 2

start_seeds   = 2, 12, 41, 51, 251, 252, 253, 254, 255, 1008, 1025, 1029, 1015, 1009, 47, 46, 8, 7
stop_seeds    = 2, 12, 41, 51, 251, 252, 253, 254, 255
exclude_seeds =

## Implementation

### 1- Creation of specific masks for tractography

```python
function: seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)
seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)
whiteMatterAct = self.__extractWhiteMatterFrom5tt(tt5Resample)
```

### 2- Creation of specific masks using apar_aseg

```python
self.info(mriutil.mrcalc(aparcAsegResample, '253', self.buildName('aparc_aseg', ['253', 'mask'], 'nii.gz')))
self.info(mriutil.mrcalc(aparcAsegResample, '1024', self.buildName('aparc_aseg', ['1024', 'mask'],'nii.gz')))
```

## Expected result(s) - Quality Assessment (QA)

- Produce an image (png) of the white matter

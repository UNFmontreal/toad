# Upsampling
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Upsampling                                            |
|**Goal**        | Upsampling of the diffusion-weigthed images           |
|**Config file** | `voxel_size` <br />`b0_extract_at_axis`<br />'cleanup`|
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weigthed upsampled images                   |

# 

## Goal

The upsampling tasks creates diffusion-weigthed images (DWI) upsampled to anatomical images resolution

## Requirements

- Diffusion-weigthed images (dwi)
- 

## Config file parameters

[what are the options in the config file -- see parameters in the table]

#upsampling voxel size in x y z direction suited for upsampling
voxel_size: 1 1 1

#extract B0
#extract_at_axis: {1, 2 , 3}
#        "Extract data only at the coordinates specified. This option
#        specifies the Axis. Must be used in conjunction with
#        extract_at_coordinate.
b0_extract_at_axis: 3


#remove extra files
cleanup: True

## Implementation

### 1- Upsampling

```R
function: dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weigthed upsampled images
- Creation of an image (png) of DWI and an image (png) of the b0 


# Upsampling
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Upsampling                                            |
|**Goal**        | Upsampling of the diffusion-weigthed images                                 |
|**Parameters**  | Diffusion-weigthed images                               |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion-weigthed upsampled images                            |

## Goal

Upsampling task creates diffusion-weigthed images (DWI) upsampled to anatomical images resolution

## Requirements

- Diffusion-weigthed images (dwi)
- 
## Parameters

Resolution of the anatomical image

## Implementation

### 1- Upsampling

```
function: dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion-weigthed upsampled images
- Creation of a png of DWI and a png of the b0 


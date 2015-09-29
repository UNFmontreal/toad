# Upsampling
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Upsampling                                            |
|**Goal**        | Upsampling of the dwi                                 |
|**Parameters**  | Diffusion images (dwi)                                |
|**Time**        | N/A                                                   |
|**Output**      | Diffusion upsampled images                            |

## Goal

Upsampling task creates diffusion images upsampled to anatomical images resolution


## Requirements

Diffusion images (dwi)

## Parameters

Resolution of the anatomic

## Implementation

### [1- Step 1 name]

```
function: dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
```

## Expected result(s) - Quality Assessment (QA)

- Diffusion weigthed images upsampled
- Creation of a png of dwi and a png of the b0 


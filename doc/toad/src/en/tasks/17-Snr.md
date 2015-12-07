# SNR
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | SNR                                                   |
|**Goal**        | Assessment of the SNR                                 |
|**Parameters**  | `ignore`                                              |
|**Time**        | N/A                                                   |
|**Output**      | QA images                                             |

#

## Goal

The SNR step creates several graphs to assess the Signal to Noise Ratio of the DWI data.

## Config file parameters

Ignore snr task

- `ignore: False`

## Minimal Requirements

- Native diffusion-weigthed images
- Corpus Callusum mask
- Brain mask

## Optimal Requirements

- Denoised diffusion-weigthed images
- Corrected diffusion-weigthed images

## Implementation


## Expected result(s) - Quality Assessment (QA)

- SNR for each directions of the diffusion-weigthed images
- Noise profile
- Noise mask used to extract noise data
- Corpus Callusum mask to extract signal data

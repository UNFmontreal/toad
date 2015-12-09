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

## Minimum Requirements

- Native diffusion-weighted images
- Corpus callosum mask
- Brain mask

## Optimal Requirements

- Denoised diffusion-weighted images
- Corrected diffusion-weighted images

## Implementation


## Expected result(s) - Quality Assessment (QA)

- SNR for each direction of the diffusion-weighted images
- Noise profile
- Noise mask used to extract noise data
- Corpus callosum mask to extract signal data


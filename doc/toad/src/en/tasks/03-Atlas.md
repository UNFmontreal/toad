# Atlas - This step has been disabled
---

|                |                                                       |
|----------------|-------------------------------------------------------|
|**Name**        | Atlas                                          |
|**Goal**        | Create atlases using Freesurfer tempalte                               |
|**Config file** | N/A|
|**Time**        | Few minutes                                        |
|**Output**      | - 7networks atlas<br> - AAL2 atlas     |

#

## Goal

The atlas step creates the required atlas using Freesurfer functions. 

## Requirements

- Anatomical image (anat)
- Freesurfer pipeline

## Config file parameters

- `cleanup: True`

## Implementation

### 1- Creation of atlases using Freesurfer template

- function: self.__createImageFromAtlas("template_aal2", self.get("aal2"))

## Expected result(s) - Quality Assessment (QA)

- AAL2, Choi, Yeo and Buckner atlases will be created.
- Choi, Yeo and Buckner have been merged into one atlas renamed 7networks.

## References

### Associated documentation

- <a href="https://surfer.nmr.mgh.harvard.edu/fswiki/CorticalParcellation_Yeo2011" target="_blank">Atlas Yeo</a>
- <a href="http://surfer.nmr.mgh.harvard.edu/fswiki/CerebellumParcellation_Buckner2011" target="_blank">Atlas Buckner</a>
- <a href="http://surfer.nmr.mgh.harvard.edu/fswiki/StriatumParcellation_Choi2012" target="_blank">Atlas Choi</a>
- <a href="http://www.gin.cnrs.fr/AAL2" target="_blank">Atlas AAL2</a>


### Articles

- Buckner, R. L., Krienen, F. M., Castellanos, a, Diaz, J. C., & Yeo, B. T. T. (2011). The organization of the human cerebellum estimated by intrinsic functional connectivity. Journal of Neurophysiology, 106(5), 2322-2345.

- Yeo, B. T., Krienen, F. M., Sepulcre, J., Sabuncu, M. R., Lashkari, D., Hollinshead, M., Roffman, J. L., et al. (2011). The organization of the human cerebral cortex estimated by intrinsic functional connectivity. J Neurophysiol, 106(3), 1125-1165. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/21653723

- Rolls, E. T., Joliot, M., & Tzourio-Mazoyer, N. (2015). Implementation of a new parcellation of the orbitofrontal cortex in the automated anatomical labeling atlas. NeuroImage, 122, 1-5. Retrieved from http://www.ncbi.nlm.nih.gov/pubmed/26241684



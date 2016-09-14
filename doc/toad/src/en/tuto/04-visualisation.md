# Processed images: visualization

The TOAD team recommends using two main programs to visualize the data:

1. **`freeview`** (dépendence de `FreeSurfer`) for all anatomical and diffusion images, segmentations or masks

2. **`fibernavigator`** to visualize the streamlines

These two programs are available for free on the Internet and are also installed on the UNF servers, and thus accessible through an ssh connection with the '-Y' option.

***If you are using images issued from fibernavigator, you must add this reference to your paper:***  *Chamberland M., Whittinstall K., Fortin D., Mathieu D., and Descoteaux M., "Real-time multi-peak tractography for instantaneous connectivity display." Frontiers in Neuroinformatics, 8 (59): 1-15, 2014.*



***It is of the utmost importance to verify your images at each step and not only those that will serve for the analysis. As a reminder, you should always verify your data before launching an analysis or preprocessing of any kind, TOAD included.***

Pour all visualizations, **you must connect via the UNF servers** (Stark ou Magma) through an ssh connection : `ssh -Y username@stark.criugm.qc.ca`.
The commands presented below are to be executed from the walking directory of a given TOAD participant (the `toad_data` folder by default).

<!-- FIXME add cross-ref -->


## 01-Preparation
To visualize the raw data:

```bash
# Anatomical data
freeview 01-preparation/anat_*.nii.gz

# Diffusion data
freeview 01-preparation/dwi_*.nii.gz

# B0s with a different encoding phase
freeview 01-preparation/b0_ap_*.nii.gz
freeview 01-preparation/b0_pa_*.nii.gz
```

You can navigate through the different volumes using `frame` option, depending on the gradient directions.
If the contrast intensity is too weak (non-visible or weakly visible images), modify the 'Max' option on the bottom left (e.g. set to 500).

You must look for eventual artefacts due to acquisition (holes, deformations, aberrant signals) and movements that are too great between volumes.
You may also verify the B0 AP et PA images in terms of the position of the anterior/posterior deformation.

<!-- FIXME cf interface, termes et description -->

## 02-Segmentation
Visualizing segmented data is done with the following commands:

```bash
# Brain mask
freeview 02-parcellation/anat_*.nii.gz `ls 02-parcellation/brain_mask*.nii.gz`:opacity=0.25

# Segmentation
freeview 02-parcellation/anat_*.nii.gz -v 02-parcellation/aparc_aseg.nii.gz:colormap=lut:opacity=0.25
```

<!-- cf add commands in terms of files + Add the links -->

If you encounter preprocessing difficulties, we recommend you verify the documentation and the mailing list de <a
 href="https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI" target="_blank">Freesurfer</a>  and contact the members of TOAD on the mailing list as  last resort.

## 04-Denoising
If you have denoised your data, it is extremely important to validate this correction by visualizing your data:

```bash
freeview `ls 00-backup/dwi_*.nii.gz`:grayscale=0,500 `ls 04-denoising/dwi_*_denoise.nii.gz`:grayscale=0,500
```

Change to make once the interface is open:

`Frame` = minimum 2

**You must pass from one image to the next** (dwi and denoised) by checking off the image in which you wish to navigate.

<!-- Change the frames (other directions). Pay attention because you must change both images. Change with check/uncheck and control to change Max -->

## 05-Correction
Corrections made to the diffusion images can be visualized with the following commands:
```bash
# For denoised images
freeview 04-denoising/dwi_*_denoise.nii.gz 05-correction/dwi_*_eddy_corrected.nii.gz

# For non-denoised images
freeview 00-backup/dwi_*.nii.gz 05-correction/dwi_*_eddy_corrected.nii.gz
```

The same verifications & options as proposed for denoising (denoising, previous section) are applied here.

## 07-Registration
The coregistration of the anatomical and diffusion images is visible with the following command:
```bash

freeview 07-registration/anat_*_resample.nii.gz `ls 06-upsampling/b0_*_denoise_*upsample.nii.gz`:opacity=0.60
```

As for before, you can manipulate the opacity to verify if the images are properly registered.

## 10-Tensorfsl - 11-Tensormrtrix - 12-TensorDipy

You can visualize if the tensor reconstruction indeed corresponds to your DWI data:

```bash
# Sum of Squares Errors map (sse)
freeview 10-tensorfsl/dwi_*_sse.nii.gz
```

Vous avez ensuite plusieurs façon de visualiser les tenseurs:
```bash
# FSL
fslview 10-tensorfsl/*fa.nii.gz 10-tensorfsl/*v1.nii.gz
# i --> Display as Lines (RGB)

# Freeview
freeview 10-tensorfsl/*fa.nii.gz  `ls 10-tensorfsl/*v1.nii.gz`:render=line:inversion=z

# Fibernavigator
fibernavigator 12-tensordipy/*fa.nii.gz
# Option --> Color Maps -> Grey
# File --> Open 12-tensordipy/*tensor.nii.gz (to see the tensors)
# Display --> Maximas (to see the tensors in stick form)
# File --> Open 12-tensordipy/*tensor_rgb.nii.gz (to see the RGB card)

# The tensor and/or RGB cards must have the corpus callosum in red, the corticopsinal in violet/blue and the anterior to posterior bundles in green

```

## 13-HardiMRtrix - 14-HardiDipy
The HARDI modelling can be visualized with the following command:
```bash
fibernavigator 07-regitration/anat_*.nii.gz

# Option -> Color Maps -> Grey
# File -> Open 14-hardidipy/*.csd.nii.gz (very long to load)
```

# 15-TractographyMRtrix - 17-TractQuerier - 18-TractFiltering

The visualisation of the streamlines can be done with the following command:
``` bash
# Fibernavigator
fibernavigator 07-registration/anat_*.nii.gz
# File --> Open 15-tractographymrtrix/*.tck (ou trk)
# File --> Open 17-tractquerier/*.trk
# File --> Open 18-tractfiltering/raw/outlier_cleaned_tracts/*.trk
```

# Tutorials Fibernavigator
<a href="http://www.youtube.com/watch?feature=player_embedded&v=8X_eOB9zYU8
" target="_blank"><img src="http://img.youtube.com/vi/8X_eOB9zYU8/0.jpg"
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>

# Tutorials Freesurfer
<a href="http://www.youtube.com/watch?feature=player_embedded&v=8Ict0Erh7_c
" target="_blank"><img src="http://img.youtube.com/vi/8Ict0Erh7_c/0.jpg"
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>

# Other programs to visualize data

<a href="http://www.mrtrix.org/" target="_blank">MRtrix</a>,  <a href="http://trackvis.org/docs/?subsect=instructions" target="_blank">TrackVis</a>

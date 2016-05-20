<h3>Acquisition</h3>

<p>T1 and diffusion weighed images (DWI) were acquired with
a {{number_array_coil}}-channel head coil and a {{magneticfieldstrenght}}T {{manufacturer}} {{mrmodel}} magnetic resonance
imaging system. Anatomical images were acquired using the following parameters: FoV {{t1_fov}} mm<sup>2</sup>, matrix size {{t1_matrixsize_1}} x {{t1_matrixsize_2}}, {% if t1_voxelsize_iso%} {{t1_voxelsize_1}} mm isotropic resolution {%else%} {{t1_voxelsize_1}} x {{t1_voxelsize_2}} x {{t1_voxelsize_3}} mm<sup>3</sup> voxel size {%endif%}, TE/TI/TR = {{t1_te}}/{{t1_ti}}/{{t1_tr}} ms, flip angle {{t1_flipangle}} &deg and {{t1_numberslices}} slices. 
Single shot diffusion weighted spin echo-planar imaging data was acquired using the following parameters: FoV {{dwi_fov}} mm<sup>2</sup>, matrix size {{dwi_matrixsize_1}} x {{dwi_matrixsize_2}}, {% if t1_voxelsize_iso%} {{dwi_voxelsize_1}} mm isotropic resolution {%else%} {{dwi_voxelsize_1}} x {{dwi_voxelsize_2}} x {{dwi_voxelsize_3}} mm<sup>3</sup> voxel size {%endif%}, TR/TE = {{dwi_tr}}/{{dwi_te}} ms, flip angle {{dwi_flipangle}} &deg and {{dwi_numberslices}} slices. DWI were acquired along {{dwi_numdirections}} independent directions, with a b-value of {{dwi_bvalue}}s/mm<sup>2</sup>. 

{% if (correctionMethod == 'topup'): %}
    A pair of b = 0 with no diffusion weigthing and opposite phase encode polarity were acquired to allow us susceptibility distortion correction. 
{% elif (correctionMethod == 'fieldmap'): %} 
A reference image with no diffusion weighted was acquired. Fieldmaps were also acquired to correct for distortion caused by magnetic field inhomogeneities.
{% endif %}
</p>

<h3>Prepocessing</h3>

<p>
{% if not denoising_ignore %}First, DWI were denoised using {{algorithm}} method [{{denoising_ref}}].{%endif%}{% if not correction_ignore and not denoising_ignore %} Then, they {% elif not correction_ignore %} First, DWI{%endif%}{% if not correction_ignore %} were corrected using {{denoising_algo}} method {{denoising_ref}}.{%endif%}{% if not correction_ignore %}Gradient directions were corrected corresponding to motion correction parameters.{%endif%}{% if not correction_ignore %} Motion-corrected images {%else%} DWI {%endif%}were upsampled using trilinear interpolation (upsampled to anatomical resolution).

Anatomical image went through Freesurfer's pipeline {{seg_ref}} in order to be used in the Anatomically-Constrained Tractography (ACT). T1 image was registered to the DWI {%if correction%}motion-corrected {%endif%}images. 

{% if not tensorfsl_ignore or not tensordipy_ignore or not tensormrtrix_ignore%}Eigenvectors, eigenvalues, fractional anisotropy (FA), radial diffusivity (RD), axial diffusivity (AD) and mean diffusivity (MD) were extracted from tensor reconstruction using {% if not tensorfsl_ignore%} FDT toolbox from FSL {{fsl_vers}} using {{tensorfsl_fitMethod}} method {%elif not tensordipy_ignore%} DIPY {{dipy_vers}} using {{tensordipy_fitMethod}} method {{tensordipy_ref}} {%elif not tensormrtrix_ignore%} MRtrix {{mrtrix_vers}} using {{tensormrtrix_fitMethod}} method [{{tensormrtrix_ref}}].{%endif%}{%endif%}

Fiber orientation distribution function (fODF) reconstruction was done using 

TractographyBlabla tractography, tractometer, tractofiltering

<p>These tools were wrapped in the TOAD pipeline developed in the Functional Neuroimaging Unit (UNF) from the Centre de Recherche de l'Institut Universitaire de Geriatrie de Montreal (<a href='http://www.unf-montreal.ca/toad'>http://www.unf-montreal.ca/toad</a>)</p>

<h3>References</h3>

{{references}}

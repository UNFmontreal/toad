<h3>Acquisition</h3>

<p>T1 and diffusion weighed images (DWI) were acquired with
a {{number_array_coil}}-channel head coil and a {{magneticfieldstrenght}}T {{manufacturer}} {{mrmodel}} magnetic resonance
imaging system (T1: TR= {{t1_tr}} ms, TE = {{t1_te}} ms, TI = {{t1_ti}} ms, Flip Angle =
{{t1_flipangle}} &deg;, {{t1_slices}} slices, FoV = {{t1_fov}} mm<sup>2</sup>, matrix size = {{t1_mat}}, voxel size = {{t1_voxelsize}}
 mm<sup>3</sup>; DWI: TR = {{dwi_tr}} ms, TE = {{dwi_te}} ms, Flip Angle = {{dwi_flipangle}} &deg;, voxel size:
{{dwi_voxelsize}} mm<sup>3</sup>, no gap). The DWI corresponded to a high angular resolution
diffusion MRI (HARDI) acquisition using spin echo EPI diffusion-encoded
images was performed along {{dwi_numdirections}} independent directions, with b-value of {{dwi_bvalue}}
s/mm<sup>2</sup>.</p>

<h3>Prepocessing</h3>

{% if denoising %}
<p>Denoising of DWI was done using {{algorithm}} method [{{denoising_ref}}].</p>
{% else %}
<p>DWI images were not denoised.</p>
{% endif %}

{% if correction %}
<p>DWI images were corrected using the {{correction_method}} method.</p>
{% else %}
<p>DWI images were not corrected.</p>
{% endif %}

<p>The FMRIB Diffusion toolbox EDDY of FSL {{fsl_vers}} {{fsl_ref}} was used to correct all images for subject movement and eddy-currents. Gradient directions were corrected corresponding to motion correction parameters.</p>

<p>DWI were upsampled to 1mm isotropic resolution using a trilinear interpolation {{tri_ref}}. Eigenvector, eigenvalues, fractional anisotropy (FA) were finally extracted from tensor model using FDT {{fdt_ref}} toolbox from FSL.
T1 image went through Freesurfer's pipeline {{seg_ref}} to get a segmentation of the corpus callosum. T1-weighted image was registered to the DWI using FSL.</p>

<p>These tools were wrapped in the TOAD pipeline developed in the Functional Neuroimaging Unit (UNF) from the Centre de Recherche de l'Institut Universitaire de Geriatrie de Montreal (<a href='http://www.unf-montreal.ca/toad'>http://www.unf-montreal.ca/toad</a>)</p>

<h3>References</h3>

{{references}}

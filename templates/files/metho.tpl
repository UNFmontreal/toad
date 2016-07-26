<h3>Acquisition</h3>

<p>T1 and diffusion weighed images (DWI) were acquired with
a {{number_array_coil}}-channel head coil and a {{magneticfieldstrength}}T {{manufacturer}} {{mrmodel}} magnetic resonance
imaging system. Anatomical images were acquired using the following parameters: FoV {{t1_fov}} mm<sup>2</sup>, matrix size {{t1_matrixsize_1}} x {{t1_matrixsize_2}},{%if t1_voxelsize_iso%} {{t1_voxelsize_1}} mm isotropic resolution {%else%} {{t1_voxelsize_1}} x {{t1_voxelsize_2}} x {{t1_voxelsize_3}} mm<sup>3</sup> voxel size {%endif%}, TE/TI/TR = {{t1_te}}/{{t1_ti}}/{{t1_tr}} ms, flip angle {{t1_flipangle}} &deg. 
Single shot diffusion weighted spin echo-planar imaging data was acquired using the following parameters: FoV {{dwi_fov}} mm<sup>2</sup>, matrix size {{dwi_matrixsize_1}} x {{dwi_matrixsize_2}},{% if t1_voxelsize_iso%} {{dwi_voxelsize_1}} mm isotropic resolution{%else%} {{dwi_voxelsize_1}} x {{dwi_voxelsize_2}} x {{dwi_voxelsize_3}} mm<sup>3</sup> voxel size{%endif%}, TR/TE = {{dwi_tr}}/{{dwi_te}} ms, flip angle {{dwi_flipangle}} &deg. DWI were acquired along {{dwi_numdirections}} independent directions, with a b-value of {{dwi_bvalue}}s/mm<sup>2</sup>.{%if correction_method=='topup'%} A pair of b = 0 images with no diffusion weigthing and opposite phase encode polarity were acquired to allow us susceptibility distortion correction.{%elif correction_method=='fieldmap'%} A reference image with no diffusion weighted was acquired. Fieldmaps were also acquired to correct for distortion caused by magnetic field inhomogeneities.{%endif%}
</p>

<h3>Prepocessing</h3>

<p>

{{methodology}}

<p>These tools were wrapped in the TOAD pipeline developed in the Functional Neuroimaging Unit (UNF) from the Centre de Recherche de l'Institut Universitaire de Geriatrie de Montreal (<a href='http://www.unf-montreal.ca/toad'>http://www.unf-montreal.ca/toad</a>)</p>

<h3>References</h3>

{{allReferences}}

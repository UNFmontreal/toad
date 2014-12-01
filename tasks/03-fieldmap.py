from generic.generictask import GenericTask

__author__ = 'desmat'

class Fieldmap(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, "preparation", "parcellation")


    def implement(self):
        """Placeholder for the business logic implementation

        """

	"""
        ## fieldmap create

        mag = self.getImage(self.dependDir, "mag")
        anat = self.getImage(self.dependDir, "anat")
        anatFreesurfer = self.getImage(self.parcellationDir,'anat_freesurfer')

        self.__computeFieldmap

        self.__coregisterFieldmapToAnat(mag, anatFreesurfer)
        self.__invertFieldmapToAnat()
        self.__interpolateAnatMaskToFieldmap(anat, mag)
	"""
	print "NotImplemented"
    def __coregisterFieldmapToAnat(self, source, reference):
        #flirt -in $mag -ref $anat -out  $target -omat fieldmap2t1.mat -cost normmi -searchcost normmi -dof 6 -searchrx -5 5 -searchry -5 5 -searchrz -5 5 -usesqform
        target = self.getTarget(source, "flirt")
        cmd = "flirt -in {} -ref {} -out {} -omat {} -cost{} -searchcost {} -dof {} -searchrx {} -searchry {} -searchrz {} "\
            .format(source, reference , target,
                    self.get("matrix"), self.get("cost"), self.get("searchcost"), self.get("dof"),
                    self.get("searchrx"), self.get("searchry"), self.get("searchrz"))

        if self.getBoolean("usesqform"):
            cmd += "-usesqform "

        self.launchCommand(cmd)


    def __invertFieldmapToAnat(self):

        # invert fieldmap to T1 matrix
        cmd = "convert_xfm -omat {} -inverse {}".format(self.get("inverseMatrix"), self.get("matrix"))
        self.launchCommand(cmd)


    def __interpolateAnatMaskToFieldmap(self, source, mag ):

        # interpolate T1 mask in fieldmap space
        target = self.getTarget(source, "flirt")
        outputMatrix =self.getTarget(source, "flirt", "mat")
        
        #flirt -in  anat -ref _mag.nii.gz -out anat_flirt.nii.gz -omat HC_AM32_1_mask_crop_flirt.mat -applyxfm -datatype char -init fieldmap2t1_inv.mat   -interp nearestneighbour

        cmd = "flirt -in {} -ref {} -out {} -omat {} -init {} -interp {} -datatype {} ".format("source anatomivalMask???", mag, target, outputMatrix, self.get("inverseMatrix"),self.get("interp"), self.get("datatype"))

        if self.getBoolean("applyxfm"):
            cmd += "-applyxfm "

        self.launchCommand(cmd)

    def __computeFiledmap(self):

        source = self.getImage(self.workingDir, 'anat', 'flirt')

        reg = self.getTarget(source, 'reg')
        # compute the fieldmap
        #--asym=-0.0024600000 echo Time 1 - echoTime 2
        #is sign important and whet it mean

        #fugue --asym=-0.0024600000 --loadfmap=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field.nii.gz
        #  --savefmap=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz
        #  --mask=HC_AM32_1_mask_crop_flirt.nii.gz --smooth3=2.00
        cmd = "fugue --asym=-0.0024600000 --loadfmap={phase???} --savefmap={reg} --mask={ anatMask } --smooth3={}"





        ## epi correction

        """

        ## the following step simulate a lossy distorted image from fieldmap magnitude file to improve registration with EPI
        # compute signal loss in fieldmap space
        sigloss --te=0.094000 -i /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/make_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz -m /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/warp_t1_mask/HC_AM32_1_mask_crop_flirt.nii.gz -s /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz


        # mask the fieldmap magnitude file
        fslmaths /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/convert_fieldmap_dwi_dicom/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag.nii.gz -mul /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/warp_t1_mask/HC_AM32_1_mask_crop_flirt.nii.gz /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/mask_mag/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain.nii

        # compute the fieldmap magnitude file with signal loss
        fslmaths /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/mask_mag/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain.nii -mul /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/fieldmap_mag_lossy/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy.nii

        #--dwell=Effective echo spacing
        #--unwarpdir=y < piege a la con
        # compute forward distortion on lossy fielmap magnitude file
        fugue --dwell=0.0006900000 --loadfmap=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/make_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz --in=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/fieldmap_mag_lossy/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy.nii --mask=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/warp_t1_mask/HC_AM32_1_mask_crop_flirt.nii.gz --nokspace --unwarpdir=y --warp=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy_warped.nii.gz

        # coregister the epi with lossy distorted fieldmap magnitude
        flirt -in /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/dwi_convert/20120913_131105DTIb0Saads007a1001.nii -ref /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/fm_voxelshiftmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy_warped.nii.gz -out 20120913_131105DTIb0Saads007a1001_flirt.nii.gz -omat epi_to_b0fm -cost normmi -searchcost normmi -dof 6 -interp trilinear -refweight /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz -searchrx -5 5 -searchry -5 5 -searchrz -5 5

        # invert the previously computed matrix
        convert_xfm -omat /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/invert_warp/epi_to_b0fm_inv.mat -inverse /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/estimate_warp/epi_to_b0fm

        ## get the fielmap in EPI space
        # interpolate fieldmap lossy distorted fieldmap magnitude in EPI space (just to check registration)
        flirt -in /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz -ref /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/dwi_convert/20120913_131105DTIb0Saads007a1001.nii -out fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss_flirt.nii.gz -omat fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss_flirt.mat -applyxfm -init /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/invert_warp/epi_to_b0fm_inv.mat

        # interpolate the fieldmap in EPI space
        flirt -in /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/make_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz -ref /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/dwi_convert/20120913_131105DTIb0Saads007a1001.nii -out fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_flirt.nii.gz -omat fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_flirt.mat -applyxfm -init /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/invert_warp/epi_to_b0fm_inv.mat


        ## perform distortion correction
        # compute voxel shift map in EPI space and apply correction to B0 image
        fugue --dwell=0.0006900000 --loadfmap=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/warp_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_flirt.nii.gz --in=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/dwi_convert/20120913_131105DTIb0Saads007a1001.nii --mask=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/mask2epi/HC_AM32_1_mask_crop_flirt.nii.gz --saveshift=vsm_epi.nii.gz --unwarpdir=y --unwarp=20120913_131105DTIb0Saads007a1001_unwarped.nii.gz


        # apply distortion correction to the whole DWI data
        fugue --in=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/eddy/eddy_corrected.nii.gz --mask=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/_subject_HC_AM32_1/mask2epi/HC_AM32_1_mask_crop_flirt.nii.gz --loadshift=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/epi_voxelshiftmap/vsm_epi.nii.gz --unwarp=eddy_corrected_unwarped.nii.gz
        """


        print "this is o.k."
        import sys
        sys.exit()



    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """
        return True


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return True

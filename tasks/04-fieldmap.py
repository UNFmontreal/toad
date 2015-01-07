from lib.generictask import GenericTask
from lib import util, mriutil
import scipy.ndimage
import nibabel
import numpy
import math
import os

__author__ = 'desmat'

class Fieldmap(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, "preparation", "parcellation", "eddy")

    def implement(self):

        ## fieldmap create
        dwi =  self.getImage(self.eddyDir, "eddy")
        bVal=  self.getImage(self.eddyDir, 'grad',  None, 'bval')

        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVal))

        mag = self.getImage(self.dependDir, "mag")
        phase = self.getImage(self.dependDir, "phase")
        anat = self.getImage(self.dependDir, "anat")
        anatFreesurfer = self.getImage(self.parcellationDir, 'anat_freesurfer')
        aparcAseg = self.getImage(self.parcellationDir, 'aparc_aseg')
        mask = self. __createSegmentationMask(aparcAseg)

        phaseRescale = self.__rescaleFieldMap(phase)
        fieldmapToAnat = self.__coregisterFieldmapToAnat(mag, anatFreesurfer)
        invertFielmapToAnat = self.__invertFieldmapToAnat(fieldmapToAnat)
        interpolateMask = self.__interpolateAnatMaskToFieldmap(anat, mag, invertFielmapToAnat, mask)
        fieldmap = self.__computeFieldmap(phaseRescale, interpolateMask)

        lossy = self.__simulateLossyMap(fieldmap, interpolateMask)
        magnitudeMask = self.__computeMap(self, mag, interpolateMask, 'brain')
        lossyMagnitude = self.__computeMap(self, magnitudeMask, lossy, 'lossy')

        warped = self.__computeForwardDistorsion(self, fieldmap, lossyMagnitude, magnitudeMask)

        matrixName = self.buildName("epi_to_b0fm")
        self.__coregisterEpiLossyMap(b0, warped, matrixName, lossy)
        invertMatrixName = self.__invertComputeMatrix(matrixName)
        self.__interpolateFieldmapInEpiSpace(lossy, b0, invertMatrixName)
        interpolateFieldmap = self.__interpolateFieldmapInEpiSpace(fieldmap, b0, invertMatrixName)
        saveshift = self.__performDistortionCorrection(b0, interpolateFieldmap, interpolateMask )
        self.__performDistortionCorrectionToDWI(dwi, interpolateMask, saveshift)


    #@TODO change rebase name
    def __rescaleFieldMap(self, source):

        target = self.buildName(source, 'rescale')
        try:
            deltaTE = float(self.get("dwell_time"))
        except ValueError:
            deltaTE = 0.00246

        cmd = "fslmaths {} -mul {} -div {} {} -odt float".format(source, math.pi, 4096 *deltaTE, target)
        self.launchCommand(cmd)

        return target


    def __createSegmentationMask(self, source):
        target = self.buildName(source, 'mask')

        nii = nibabel.load(source)
        op = ((numpy.mgrid[:5,:5,:5]-2.0)**2).sum(0)<=4
        mask = scipy.ndimage.binary_closing(nii.get_data()>0, op, iterations=2)
        scipy.ndimage.binary_fill_holes(mask, output=mask)
        nibabel.save(nibabel.Nifti1Image(mask.astype(numpy.uint8), nii.get_affine()), target)
        del nii, mask, op
        return target



    def __coregisterFieldmapToAnat(self, source, reference):

        target = self.buildName(source, "flirt")

        cmd = "flirt -in {} -ref {} -out {} -omat {} -cost {} -searchcost {} -dof {} "\
            .format(source, reference , target,
                    self.get("matrix"), self.get("cost"), self.get("searchcost"), self.get("dof"))

        if self.getBoolean("usesqform"):
            cmd += "-usesqform "

        self.launchCommand(cmd)
        return target


    def __invertFieldmapToAnat(self, source):

        target = self.buildName(source, 'inv', 'mat')
        cmd = "convert_xfm -omat {} -inverse {}".format(target , source)
        self.launchCommand(cmd)
        return target


    def __interpolateAnatMaskToFieldmap(self, source, mag, inverseMatrix,  mask):

        # interpolate T1 mask in fieldmap space
        target = self.buildName(source, "flirt")
        outputMatrix =self.buildName(source, "flirt", "mat")
        
        #flirt -in  anat -ref _mag.nii.gz -out anat_flirt.nii.gz -omat HC_AM32_1_mask_crop_flirt.mat -applyxfm -datatype char -init fieldmap2t1_inv.mat   -interp nearestneighbour

        cmd = "flirt -in {} -ref {} -out {} -omat {} -init {} -interp {} -datatype {} "\
            .format(mask, mag, target, outputMatrix, inverseMatrix, self.get("interp"), self.get("datatype"))

        if self.getBoolean("applyxfm"):
            cmd += "-applyxfm "

        self.launchCommand(cmd)
        return target


    def __computeFiledmap(self, source, mask):

        target = self.buildName(source, 'reg')

        # compute the fieldmap
        #--asym=-0.0024600000 echo Time 1 - echoTime 2

        #fugue --asym=-0.0024600000 --loadfmap=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field.nii.gz
        #  --savefmap=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz
        #  --mask=HC_AM32_1_mask_crop_flirt.nii.gz --smooth3=2.00

        cmd = "fugue --asym={} --loadfmap={} --savefmap={} --mask={} --smooth3={}"\
            .format(self.get("dwell_time"), source, target,  mask, self.get("smooth3"))

        self.launchCommand(cmd)
        return target


    def __simulateLossyMap(self, source, mask):

        ## the following step simulate a lossy distorted image from fieldmap magnitude file to improve registration with EPI
        # compute signal loss in fieldmap space
        #sigloss --te=0.094000 -i /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/make_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz -m /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/warp_t1_mask/HC_AM32_1_mask_crop_flirt.nii.gz -s /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz

        target = self.buildName(source, 'sigloss')
        cmd = "sigloss --te={} -i {} -m {} -s".format(self.get('echo_time'), source, mask, target)

        self.launchCommand(cmd)
        return target


    #@TODO find another prefix instead of mask and suffix brain
    def __computeMap(self, source, mask, prefix):

        # compute the fieldmap magnitude file with signal loss
        #fslmaths /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/mask_mag/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain.nii -mul /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/signal_loss/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg_sigloss.nii.gz /media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/fieldmap_mag_lossy/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy.nii

        target = self.buildName(source, prefix)

        cmd = "fslmaths {} -mul {} ".format(source, mask, target)
        self.launchCommand(cmd)

	
    def __computeForwardDistorsion(self, source, lossyImage, mask):
        #--dwell=Effective echo spacing
        #--unwarpdir=y < piege a la con
        # compute forward distortion on lossy fielmap magnitude file
        #fugue --dwell=0.0006900000 --loadfmap=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/make_fieldmap/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_field_reg.nii.gz --in=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/epi_correction/_subject_HC_AM32_1/fieldmap_mag_lossy/fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy.nii --mask=/media/77f462a2-7290-437d-8209-c1e673ed635a/analysis/cardio_pd/dwi_fieldmap/_subject_HC_AM32_1/warp_t1_mask/HC_AM32_1_mask_crop_flirt.nii.gz --nokspace --unwarpdir=y --warp=fieldmap_dwi_CARDIO_HC_C_AM32_1_20120913_mag_brain_lossy_warped.nii.gz


        target = self.buildName(source, 'warped')
        cmd = "fugue --dwell={} --loadfmap={} --in={} --mask={}  --nokspace --unwarpdir={} --warp={} ".format(self.get('dwell_time'), source, lossyImage, self.get('unwarpdir'), target )
        self.launchCommand(cmd)
        return target


    def __coregisterEpiLossyMap(self, source, reference, matrix, weighted ):
        "flirt -in {} -ref {} -omat {} -cost normmi -searchcost normmi -dof {} -interp trilinear -refweight {} ".format(source, reference, matrix, self.get("dof"), weighted)


    def __invertComputeMatrix(self, source):

        target = self.buildName(source, 'inv', 'mat')
        cmd = "convert_xfm -omat {} -inverse {}".format(target , source)
        self.launchCommand(cmd)
        return target


    def __interpolateFieldmapInEpiSpace(self, source, reference, initMatrix):
        target = self.buildName(source, 'sigloss')
        outputMatrixName = self.buildName(source, 'flirt', 'mat')

        cmd = "flirt -in {} -ref {} -out {} -omat {} -applyxfm -init {}".format(source, reference, outputMatrixName, initMatrix)
        self.launchCommand(cmd)
        return target



    def __performDistortionCorrection(self, source, fieldmap, mask):

        unwarp = self.buildName(source, 'unwarped')
        target = self.buildName(source, 'vsm')
        cmd = "fugue --dwell={} --in={}  --loadfmap={}--mask={} --saveshift={} --unwarpdir={} --unwarp={}".format(source, self.get('dwell_time'), fieldmap, mask, target, self.get('unwarpdir'), unwarp)
        self.launchCommand(cmd)
        return target


    def __performDistortionCorrectionToDWI(self, source, mask, shift):

        target = self.buildName(source, 'unwarped')
        cmd= "fugue --in={} --mask={} --loadshift={} --unwarp={}".format(source, mask, shift, target)
        self.launchCommand(cmd)
        return target



    def isIgnore(self):
        return self.isSomeImagesMissing({'magnitude':self.getImage(self.dependDir, 'mag'), 'phase':self.getImage(self.dependDir, 'phase')})


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

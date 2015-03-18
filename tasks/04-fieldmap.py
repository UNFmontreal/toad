import math
import os

import scipy.ndimage
import nibabel
import numpy

from core.generictask import GenericTask
from lib.images import Images
from lib import mriutil


__author__ = 'desmat'

class Fieldmap(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, "preparation", "parcellation", "eddy")


    def implement(self):

        if not self.config.getboolean("eddy", "ignore"):
            dwi = self.getImage(self.eddyDir, "dwi", "eddy")
            bVals=  self.getImage(self.eddyDir, 'grad',  None, 'bvals')
        else:
            dwi = self.getImage(self.preparationDir, "dwi")
            bVals=  self.getImage(self.preparationDir, 'grad',  None, 'bvals')

        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        mag = self.getImage(self.dependDir, "mag")
        phase = self.getImage(self.dependDir, "phase")
        anat = self.getImage(self.dependDir, "anat")

        freesurfer_anat = self.getImage(self.parcellationDir, 'anat', 'freesurfer')

        aparcAseg = self.getImage(self.parcellationDir, 'aparc_aseg')
        mask = self. __createSegmentationMask(aparcAseg)

        self.info("rescaling the phase image")
        phaseRescale = self.__rescaleFieldMap(phase)

        self.info('Coregistring magnitude image with the anatomical image produce by freesurfer')
        fieldmapToAnat = self.__coregisterFieldmapToAnat(mag, freesurfer_anat)

        self.info('Compute the transformation from the anatomical image produce by freesurfer to the magnitude image')
        invertFielmapToAnat =  self.buildName(fieldmapToAnat, 'inverse', 'mat')
        self.info(mriutil.invertMatrix(fieldmapToAnat, invertFielmapToAnat))

        self.info('Resampling the anatomical mask into the phase image space')
        interpolateMask = self.__interpolateAnatMaskToFieldmap(anat, phaseRescale, invertFielmapToAnat, mask)
        fieldmap = self.__computeFieldmap(phaseRescale, interpolateMask)

        lossy = self.__simulateLossyMap(fieldmap, interpolateMask)

        magnitudeMask = self.__computeMap(mag, interpolateMask, 'brain')
        lossyMagnitude = self.__computeMap(magnitudeMask, lossy, 'lossy')

        warped = self.__computeForwardDistorsion(fieldmap, lossyMagnitude, interpolateMask)

        matrixName = self.get("epiTo_b0fm")
        self.__coregisterEpiLossyMap(b0, warped, matrixName, lossy)

        invertMatrixName = self.buildName(matrixName, 'inverse', 'mat')
        self.info(mriutil.invertMatrix(matrixName, invertMatrixName))
        magnitudeIntoDwiSpace = self.__interpolateFieldmapInEpiSpace(warped, b0, invertMatrixName)
        magnitudeIntoDwiSpaceMask = self.__mask(magnitudeIntoDwiSpace)
        interpolateFieldmap = self.__interpolateFieldmapInEpiSpace(fieldmap, b0, invertMatrixName)
        saveshift = self.__performDistortionCorrection(b0, interpolateFieldmap, magnitudeIntoDwiSpaceMask)

        self.__performDistortionCorrectionToDWI(dwi, magnitudeIntoDwiSpaceMask, saveshift)


    def __getMagnitudeEchoTimeDifferences(self):
        try:
            echo1 = float(self.get("echo_time_mag1"))/1000.0
            echo2 = float(self.get("echo_time_mag2"))/1000.0
            return str(echo2-echo1)

        except ValueError:
            self.error("cannot determine difference echo time between the two magnitude image")


    def __getDwiEchoTime(self):
        try:
            echo = float(self.get("echo_time_dwi"))/1000.0
            return str(echo)

        except ValueError:
            self.error("cannot determine the echo time of the dwi image")


    def __getDwellTime(self):
        try:
            spacing = float(self.config.get("eddy","echo_spacing"))/1000.0
            return str(spacing)

        except ValueError:
            self.error("cannot determine the effective echo spacing of the dwi image")


    def __getUnwarpDirection(self):
        try:
            direction = int(self.config.get("eddy","phase_enc_dir"))
            value="y"
            if direction == 0:
                value = "y"
            elif direction == 1:
                value = "y-"
            elif direction == 2:
                value = "x-"
            elif direction == 3:
                value = "x"
            return value

        except ValueError:
            self.error("cannot determine unwarping direction of the the dwi image")


    def __rescaleFieldMap(self, source):

        target = self.buildName(source, 'rescale')
        try:
            deltaTE = float(self.__getMagnitudeEchoTimeDifferences())
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
                self.get("fieldmapToAnat"), self.get("cost"), self.get("searchcost"), self.get("dof"))

        self.launchCommand(cmd)
        return self.get("fieldmapToAnat")


    def __interpolateAnatMaskToFieldmap(self, source, mag, inverseMatrix,  mask):

        target = self.buildName(source, "mask")
        outputMatrix =self.buildName(source, "mask", "mat")
        cmd = "flirt -in {} -ref {} -out {} -omat {} -init {} -interp {} -datatype {} "\
            .format(mask, mag, target, outputMatrix, inverseMatrix, self.get("interp"), self.get("datatype"))

        if self.getBoolean("applyxfm"):
            cmd += "-applyxfm "

        self.launchCommand(cmd)
        return target


    def __computeFieldmap(self, source, mask):

        target = self.buildName(source, 'fieldmap')
        cmd = "fugue --asym={} --loadfmap={} --savefmap={} --mask={} --smooth3={}"\
            .format(self.__getMagnitudeEchoTimeDifferences(), source, target,  mask, self.get("smooth3"))

        self.launchCommand(cmd)
        return target


    def __simulateLossyMap(self, source, mask):

        target = self.buildName(source, 'sigloss')
        cmd = "sigloss --te={} -i {} -m {} -s {}".format(self.__getDwiEchoTime(), source, mask, target)
        self.launchCommand(cmd)
        return target


    def __computeMap(self, source, mask, prefix):

        target = self.buildName(source, prefix)
        cmd = "fslmaths {} -mul {} {}".format(source, mask, target)
        self.launchCommand(cmd)
        return target


    def __computeForwardDistorsion(self, source, lossyImage, mask):

        target = self.buildName(source, 'warp')
        cmd = "fugue --dwell={} --loadfmap={} --in={} --mask={}  --nokspace --unwarpdir={} --warp={} ".format(self.__getDwellTime(),source, lossyImage,  mask, self.__getUnwarpDirection(), target )
        self.launchCommand(cmd)
        return target


    def __coregisterEpiLossyMap(self, source, reference, matrix, weighted ):

        target = self.buildName(source, 'flirt')
        cmd = "flirt -in {} -ref {} -omat {} -cost normmi -searchcost normmi -dof {} -interp trilinear -refweight {} ".format(source, reference, matrix, self.get("dof"), weighted)
        self.launchCommand(cmd)
        return target


    def __interpolateFieldmapInEpiSpace(self, source, reference, initMatrix):
        target = self.buildName(source, 'flirt')
        cmd = "flirt -in {} -ref {} -out {} -applyxfm -init {}".format(source, reference, target, initMatrix)
        self.launchCommand(cmd)
        return target


    def __mask(self, source):
        target = self.buildName(source, 'mask')
        cmd = "fslmaths {} -bin {}".format(source, target)
        self.launchCommand(cmd)
        return target	


    def __performDistortionCorrection(self, source, fieldmap, mask):
        unwarp = self.buildName(source, 'unwarp')
        target = self.buildName(source, 'vsm')
        cmd = "fugue --in={}  --loadfmap={} --mask={} --saveshift={} --unwarpdir={} --unwarp={} --dwell={} "\
            .format(source,  fieldmap, mask, target, self.__getUnwarpDirection(), unwarp, self.__getDwellTime())
        self.launchCommand(cmd)
        return target


    def __performDistortionCorrectionToDWI(self, source, mask, shift):

        target = self.buildName(source, 'unwarp')
        cmd= "fugue --in={} --mask={} --loadshift={}  --unwarpdir={} --unwarp={}  "\
            .format(source, mask, shift, self.__getUnwarpDirection(), target)
        self.launchCommand(cmd)
        return target


    def isIgnore(self):
        dependImages = Images((self.getImage(self.dependDir, 'mag'), 'magnitude'), (self.getImage(self.dependDir, 'phase'),  'phase'))
        subjectImages = Images((self.getImage(self.subjectDir, 'mag'), 'magnitude'), (self.getImage(self.subjectDir, 'phase'), 'phase'))
	return not (dependImages.isAllImagesExists() or subjectImages.isAllImagesExists())

    def meetRequirement(self, result=True):
        """Validate if all requirements have been met prior to launch the task

        Returns:
            True if all requirement are meet, False otherwise
        """

        images = Images((self.getImage(self.dependDir, "dwi", 'eddy'), 'eddy corrected'))
        if images.isSomeImagesMissing():
            images = Images((self.getImage(self.preparationDir, "dwi"), 'diffusion weighed'))

        images.extend(Images((self.getImage(self.parcellationDir, 'anat', 'freesurfer'), "freesurfer anatomical"),
                              (self.getImage(self.parcellationDir, 'aparc_aseg'), "parcellation"),
                              (self.getImage(self.dependDir, 'anat'), "high resolution"),
                              (self.getImage(self.dependDir, 'mag'), "magnitude"),
                              (self.getImage(self.dependDir, 'phase'), "phase")))
        result = images.isAllImagesExists()
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution

        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        images = Images((self.getImage(self.workingDir, "dwi", 'unwarp'), 'unwarped'))
        return images.isSomeImagesMissing()

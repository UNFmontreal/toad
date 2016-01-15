# -*- coding: utf-8 -*-
import os
import math

import matplotlib

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers", "Basile Pinsard"]


matplotlib.use('Agg')

class Correction(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'parcellation', 'denoising', 'qa')
        self.__topupCorrection = False
        self.__fieldmapCorrection = False


    def implement(self):

        dwi = self.getDenoisingImage('dwi', 'denoise')
        if not dwi:
            dwi = self.getPreparationImage('dwi')

        b0AP= self.getPreparationImage('b0_ap')
        b0PA= self.getPreparationImage('b0_pa')
        bEnc=  self.getPreparationImage('grad',  None, 'b')
        bVals=  self.getPreparationImage('grad',  None, 'bvals')
        bVecs=  self.getPreparationImage('grad',  None, 'bvecs')
        norm=   self.getParcellationImage('norm')
        parcellationMask = self.getParcellationImage('mask')

        #fieldmap only
        mag = self.getPreparationImage("mag")
        phase = self.getPreparationImage("phase")
        freesurferAnat = self.getParcellationImage('anat', 'freesurfer')

        self.info("extract b0 image from the dwi")
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))


        self.info("look if all images have the same voxel size and dimension scale")
        self.__validateSizeAndDimension(dwi, b0, b0AP, b0PA)

        #Generate a missing b0 image if we could. --> 0 = P>>A, 1 = A>>P
        if self.get("phase_enc_dir") == "0" and b0AP and b0PA is False:
            
            b0PA = b0

        if self.get("phase_enc_dir") == "1" and b0PA and b0AP is False :
            b0AP = b0

        [dwi, b0, b0AP, b0PA] = self.__oddEvenNumberOfSlices(dwi, b0, b0AP, b0PA)

        if b0AP is False or b0PA is False:
            topupBaseName = None
            b0Image = b0

        else:
            #concatenate B0 image together
            if self.get("phase_enc_dir") == "0":
                concatenateB0Image = self.__concatenateB0(b0PA, b0AP, self.buildName("b0pa_b0ap", None, "nii.gz"))

            elif self.get("phase_enc_dir") == "1":
                concatenateB0Image = self.__concatenateB0(b0AP, b0PA, self.buildName("b0ap_b0pa", None, "nii.gz" ))
            #create the acquisition parameter file
            acqpTopup = self.__createAcquisitionParameterFile('topup')

            #Lauch topup on concatenate B0 image
            [topupBaseName, topupImage] = self.__topup(concatenateB0Image, acqpTopup, self.get('b02b0_filename'))
            b0Image = self.__fslmathsTmean(os.path.join(self.workingDir, topupImage))
            self.__topupCorrection = True


        self.info("create a suitable mask for the dwi")
        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform -dof 6"

        mask = mriutil.computeDwiMaskFromFreesurfer(b0Image,
                                                    norm,
                                                    parcellationMask,
                                                    self.buildName(parcellationMask, 'temporary'),
                                                    extraArgs)

        #create the acquisition parameter file for eddy
        acqpEddy = self.__createAcquisitionParameterFile('eddy')

        #create an index file
        indexFile = self.__createIndexFile(mriutil.getNbDirectionsFromDWI(dwi))

        outputImage = self.__correctionEddy2(dwi,
                                    mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)



        eddyParameterFiles = self.getImage('dwi', None, 'eddy_parameters')
        if eddyParameterFiles:
            self.info("Apply eddy movement correction to gradient encodings directions")
            bEnc = mriutil.applyGradientCorrection(bEnc, eddyParameterFiles, self.buildName(outputImage, None, 'b'))
            self.info(mriutil.mrtrixToFslEncoding(outputImage,
                                        bEnc,
                                        self.buildName(outputImage, None, 'bvecs'),
                                        self.buildName(outputImage, None, 'bvals')))



        #proceed with fieldmap if provided
        if mag and phase:
            #@TODO retirer le switch self.get("force_fieldmap")
            if not self.__topupCorrection or self.get("force_fieldmap"):
                eddyCorrectionImage = self.__correctionEddy2(dwi, mask, None, indexFile, acqpEddy, bVecs, bVals)
                outputImage = self.__computeFieldmap(eddyCorrectionImage, bVals, mag, phase, norm, parcellationMask, freesurferAnat)
                self.__fieldmapCorrection = True


        #produce a valid b0 and mask for QA
        b0Corrected = self.buildName(b0, 'corrected')
        self.info(mriutil.extractFirstB0FromDwi(outputImage, b0Corrected, bVals))
        maskCorrected = mriutil.computeDwiMaskFromFreesurfer(b0Corrected,
                                                    norm,
                                                    parcellationMask,
                                                    self.buildName(parcellationMask, 'corrected'),
                                                    extraArgs)

        self.rename(outputImage, self.buildName(outputImage, 'corrected'))


    def __oddEvenNumberOfSlices(self, *args):
        """return a list of images that will count a odd number of slices in z direction

            If an even number of slices is found, the upper volume will be remove

        Args:
            *args: a list of images

        Returns:
             a list of images stripped

        """
        output = []
        for image in args:
            if image:
                try:
                    zDims = int(mriutil.getMriDimensions(image)[2])
                    if zDims%2 == 1:
                        target = self.buildName(image, "subset")
                        mriutil.extractSubVolume(image, target, '+2',"0:{}".format(zDims-2), self.getNTreadsMrtrix())
                        output.append(target)
                    else:
                        output.append(image)
                except ValueError:
                    output.append(image)
            else:
                output.append(False)
        return output


    def __concatenateB0(self, source1, source2, target):
        """Concatenate two images along the axis 3

        Args:
            source1: The first image
            source2:  The second image
            target: The name of the resulting image

        Returns:
             The name of the resulting image
        """
        cmd = "mrcat {} {} {} -axis 3 -nthreads {} -quiet".format(source1, source2, target, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return target


    def __createAcquisitionParameterFile(self, type):
        """Create the acquire parameter (--acqp) file for topup or eddy

        For topup, the image will concatenate b0AP first then b0PA
            #A>>P, 0 -1 0
            #P>>A, 0 1 0
            #R>>L, 1 0 0
            #L>>R, -1 0 0
        Args:
            type: algorithm this file is create for. Valid value are: topup, eddy

        Returns:
            the acquisition parameter file name

        """
        try:
            phaseEncDir = int(self.get('phase_enc_dir'))
        except ValueError:
            self.error("Cannot determine the phase encoding direction")

        try:
            echoSpacing = float(self.get('echo_spacing'))
            epiFactor = int(self.get('epi_factor'))
            factor = (epiFactor-1) * (echoSpacing/1000)

        except ValueError:
            self.warning("Cannot find suitable Echo Spacing value, will use a factor of 0.1")
            factor = "0.1"

        if type=='topup':
            parameter='acqp_topup'
            text = "0 1 0 {}\n0 -1 0 {}\n".format(factor, factor)

        elif type=='eddy':
            parameter='acqp_eddy'
            text = "0 1 0 {}\n".format(factor)

        else:
            self.error("Type must be of value: topup or eddy")
            return False

        target = os.path.join(self.workingDir, self.get(parameter))
        if not util.createScript(target, text):
            self.error("Unable to create script {}".format(target))

        return target


    def __createIndexFile(self, dimensions):
        """Create the file that will contain the index

        Args:
            dimensions: the number of direction into the B0 images

        Returns:
            The resulting file name
        """
        target = os.path.join(self.workingDir, self.get( 'index_filename'))
        self.info("Creating index file {}".format(target))
        text = ""
        for i in range(0,dimensions):
            text+="1 "

        util.createScript(target, text)
        return target


    def __validateSizeAndDimension(self, *args):

        names = []
        dims = []
        sizes = []

        for source in args:
            if source:
                names.append(source)
                dimensions = mriutil.getMriDimensions(source)
                if len(dimensions) == 4:
                    dims.append([dimensions[0], dimensions[1], dimensions[2]])
                else:
                    dims.append(dimensions)
                    sizes.append(mriutil.getMriVoxelSize(source))

        if not dims[1:] == dims[:-1]:
            self.error("Dimension for each scale mismatch found between images: {}".format(", ".join(names)))

        if not sizes[1:] == sizes[:-1]:
            self.error("Voxel size mismatch found between images: {}".format(", ".join(names)))


    def __topup(self, source, acqp, b02b0File):

        self.info("Launch topup from fsl.\n")
        baseName = os.path.join(self.workingDir, self.get('topup_results_base_name'))
        output = os.path.join(self.workingDir, self.get('topup_results_output'))

        cmd = "topup --imain={} --datain={} --config={} --out={}  --iout={}"\
              .format(source, acqp, b02b0File, baseName, output)
        self.launchCommand(cmd)
        return [baseName, output]


    def __fslmathsTmean(self, source):

        target = source.replace(".nii", "_tmean.nii")
        self.info(mriutil.fslmaths(source, target, 'Tmean'))
        return target


    def __correctionEddy2(self, source, mask, topup, index, acqp, bVecs, bVals):
        """Performs eddy correction on a dwi file.

        Args:
            source:	File containing all the images to estimate distortions for
            mask:	Mask to indicate brain
            topup:  Base name for output files from topup
            index:	File containing indices for all volumes in --imain into --acqp and --topup
            acqp:	File containing acquisition parameters
            bvecs:	File containing the b-vectors for all volumes in --imain
            bvals:	File containing the b-values for all volumes in --imain

        Returns:
            The resulting file name

        """
        self.info("Launch eddy correction from fsl")
        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "eddy")
        cmd = "eddy --imain={} --mask={} --index={} --acqp={} --bvecs={} --bvals={} --out={} "\
              .format(source, mask, index, acqp, bVecs, bVals, tmp)

        if topup is not None:
            cmd += " --topup={}".format(topup)

        self.getNTreadsEddy()
        self.launchCommand(cmd, None, None, 5*60*60)
        return self.rename(tmp, target)



    def __computeFieldmap(self, dwi, bVals, mag, phase, norm, parcellationMask, freesurferAnat):

        #extract a b0 from the dwi image
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.get("prefix", 'dwi'), "b0_fieldmap_tmp"))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        self.info("rescaling the phase image")
        phaseRescale = self.__rescaleFieldMap(phase)

        self.info('Coregistring magnitude image with the anatomical image produce by freesurfer')
        fieldmapToAnat = self.__coregisterFieldmapToAnat(mag, freesurferAnat)

        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform  -dof 6"

        interpolateMask = mriutil.computeDwiMaskFromFreesurfer(mag,
                                                               norm,
                                                               parcellationMask,
                                                               self.buildName(parcellationMask, 'interpolate'),
                                                               extraArgs)

        self.info('Resampling the anatomical mask into the phase image space')
        #interpolateMask = self.__interpolateAnatMaskToFieldmap(anat, phaseRescale, invertFielmapToAnat, mask)
        fieldmap = self.__computePhaseFieldmap(phaseRescale, interpolateMask)

        self.info('Generate a lossy magnitude file with signal loss and distortion')
        lossy = self.__simulateLossyMap(fieldmap, interpolateMask)

        magnitudeMask = self.__computeMap(mag, interpolateMask, 'brain')
        lossyMagnitude = self.__computeMap(magnitudeMask, lossy, 'lossy')

        warped = self.__computeForwardDistorsion(fieldmap, lossyMagnitude, interpolateMask)

        self.info('Coregister the simulated lossy fieldmap with the EPI')
        matrixName = self.get("epiTo_b0fm")
        self.__coregisterEpiLossyMap(b0, warped, matrixName, lossy)

        self.info('Reslice magnitude and fieldmap in the EPI space')
        invertMatrixName = self.buildName(matrixName, 'inverse', 'mat')
        self.info(mriutil.invertMatrix(matrixName, invertMatrixName))
        magnitudeIntoDwiSpace = self.__interpolateFieldmapInEpiSpace(warped, b0, invertMatrixName)
        magnitudeIntoDwiSpaceMask = self.__mask(magnitudeIntoDwiSpace)
        interpolateFieldmap = self.__interpolateFieldmapInEpiSpace(fieldmap, b0, invertMatrixName)
        self.info('Create the shift map')
        saveshift = self.__performDistortionCorrection(b0, interpolateFieldmap, magnitudeIntoDwiSpaceMask)

        self.info('Perform distortion correction of EPI data')
        dwiUnwarp = self.__performDistortionCorrectionToDWI(dwi, magnitudeIntoDwiSpaceMask, saveshift)

        return dwiUnwarp

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
            spacing = float(self.get("echo_spacing"))/1000.0
            return str(spacing)

        except ValueError:
            self.error("cannot determine the effective echo spacing of the dwi image")


    def __getUnwarpDirection(self):
        try:
            direction = int(self.get("phase_enc_dir"))
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
        """
        Rescale the fieldmap to get Rad/sec
        """
        target = self.buildName(source, 'rescale')
        try:
            deltaTE = float(self.__getMagnitudeEchoTimeDifferences())
        except ValueError:
            deltaTE = 0.00246

        cmd = "fslmaths {} -mul {} -div {} {} -odt float".format(source, math.pi, 4096 *deltaTE, target)
        self.launchCommand(cmd)

        return target


    def __coregisterFieldmapToAnat(self, source, reference):
        """
        Coregister Fieldmap to T1, to get the mask in Fieldmap space
        """
        target = self.buildName(source, "flirt")
        cmd = "flirt -in {} -ref {} -out {} -omat {} -cost {} -searchcost {} -dof {} "\
            .format(source, reference , target,
                self.get("fieldmapToAnat"), self.get("cost"), self.get("searchcost"), self.get("dof"))

        self.launchCommand(cmd)
        return self.get("fieldmapToAnat")


    def __computePhaseFieldmap(self, source, mask):
        """
        Preprocess the fieldmap : scaling, masking, smoothing
        """
        target = self.buildName(source, 'fieldmap')
        cmd = "fugue --asym={} --loadfmap={} --savefmap={} --mask={} --smooth3={}"\
            .format(self.__getMagnitudeEchoTimeDifferences(), source, target,  mask, self.get("smooth3"))

        self.launchCommand(cmd)
        return target


    def __simulateLossyMap(self, source, mask):
        """
        Compute the sigloss map from the fieldmap
        """
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
        """
        Apply expected distortion to magnitude to improve flirt registration
        """
        target = self.buildName(source, 'warp')
        cmd = "fugue --dwell={} --loadfmap={} --in={} --mask={}  --nokspace --unwarpdir={} --warp={} ".format(self.__getDwellTime(),source, lossyImage,  mask, self.__getUnwarpDirection(), target )
        self.launchCommand(cmd)
        return target


    def __coregisterEpiLossyMap(self, source, reference, matrix, weighted ):
        """
        Perform coregistration of EPI onto the simulated lossy distorted fieldmap magnitude
        """
        target = self.buildName(source, 'flirt')
        cmd = "flirt -in {} -ref {} -omat {} -cost normmi -searchcost normmi -dof {} -interp trilinear -refweight {} ".format(source, reference, matrix, self.get("dof"), weighted)
        self.launchCommand(cmd)
        return target


    def __interpolateFieldmapInEpiSpace(self, source, reference, initMatrix):
        """
        Interpolate fieldmap in EPI space using flirt
        """
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
        """
        Compute the shiftmap and unwarp the B0 image
        """
        unwarp = self.buildName(source, 'unwarp')
        target = self.buildName(source, 'vsm')
        cmd = "fugue --in={}  --loadfmap={} --mask={} --saveshift={} --unwarpdir={} --unwarp={} --dwell={} "\
            .format(source,  fieldmap, mask, target, self.__getUnwarpDirection(), unwarp, self.__getDwellTime())
        self.launchCommand(cmd)
        return target


    def __performDistortionCorrectionToDWI(self, source, mask, shift):
        """
        Unwarp the whole DWI data
        """
        target = self.buildName(source, 'unwarp')
        cmd= "fugue --in={} --mask={} --loadshift={}  --unwarpdir={} --unwarp={}  "\
            .format(source, mask, shift, self.__getUnwarpDirection(), target)
        self.launchCommand(cmd)
        return target


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):

        images = Images((self.getCorrectionImage("dwi", 'corrected'), 'corrected'),
                       (self.getPreparationImage("dwi"), 'diffusion weighted'))

        if not images.isAtLeastOneImageExists():
            return False


        images = Images((self.getParcellationImage('norm'), 'freesurfer normalize'),
                        (self.getParcellationImage('mask'), 'freesurfer mask'),
                        (self.getPreparationImage('grad', None, 'bvals'), 'gradient .bvals encoding file'),
                        (self.getPreparationImage('grad', None, 'bvecs'), 'gradient .bvecs encoding file'),
                        (self.getPreparationImage('grad', None, 'b'), 'gradient .b encoding file'))

        #if fieldmap available
        if Images(self.getPreparationImage("mag") , self.getPreparationImage("phase")).isAllImagesExists():
            images.append((self.getParcellationImage('anat', 'freesurfer'),"freesurfer anatomical"))

        return images


    def isDirty(self):
        return Images((self.getImage('dwi', 'corrected'), 'diffusion weighted eddy corrected'))

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        #Get images
        dwi = self.getDenoisingImage('dwi', 'denoise')
        if not dwi:
            dwi = self.getPreparationImage('dwi')

        dwiCorrected = self.getImage('dwi', 'corrected')
        brainMask = self.getImage('mask', 'corrected')
        eddyParameterFiles = self.getImage('dwi', None, 'eddy_parameters')
        bVecs=  self.getPreparationImage('grad',  None, 'bvecs')
        bVecsCorrected = self.getImage('grad',  None, 'bvecs')

        #Build qa images
        dwiCorrectedQa = self.plot4dVolume(dwiCorrected, fov=brainMask)
        dwiCompareQa = self.compare4dVolumes(dwi, dwiCorrected,fov=brainMask)
        translationsQa, rotationsQa = self.plotMovement(
                eddyParameterFiles, dwiCorrected)
        bVecsQa = self.plotVectors(bVecs, bVecsCorrected, dwiCorrected)

        qaImages = Images(
            (dwiCorrectedQa, 'DWI corrected'),
            (dwiCompareQa, 'Before and after corrections'),
            (translationsQa, 'Translation corrections by Eddy'),
            (rotationsQa, 'Rotation corrections by Eddy'),
            (bVecsQa,
                "Gradients vectors on the unitary sphere. " \
                "Red: raw bvec | Blue: opposite bvec | " \
                "Black +: movement corrected bvec. The more corrected, " \
                "the more the + is from the center of the circle."))

        #Information on distorsion correction
        information = "Eddy movement corrections were applied to the images "
        if self.__topupCorrection:
            information += "and distortion corrections were conducted on the " \
                    "AP and PA images."
        elif self.__fieldmapCorrection:
            information += "using the fieldmap images."
        else:
            information += "with no distortion correction"
        qaImages.setInformation(information)

        return qaImages

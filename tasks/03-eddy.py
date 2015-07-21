import glob
import os

import numpy
import matplotlib
import mpl_toolkits

from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil

matplotlib.use('Agg')


__author__ = 'desmat'


class Eddy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'parcellation', 'qa')


    def implement(self):
        
        dwi = self.getImage(self.dependDir, 'dwi')
        b0AP= self.getImage(self.dependDir, 'b0_ap')
        b0PA= self.getImage(self.dependDir, 'b0_pa')
        bEnc=  self.getImage(self.dependDir, 'grad',  None, 'b')
        bVals=  self.getImage(self.dependDir, 'grad',  None, 'bvals')
        bVecs=  self.getImage(self.dependDir, 'grad',  None, 'bvecs')
        norm=   self.getImage(self.parcellationDir, 'norm')
        parcellationMask = self.getImage(self.parcellationDir, 'mask')

        #extract b0 image from the dwi
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        #make sure all the images have the same voxel size and dimension scale between them
        self.__validateSizeAndDimension(dwi, b0, b0AP, b0PA)

        #Generate a missing b0 image if we could. --> 0 = P>>A, 1 = A>>P
        if self.get("phase_enc_dir") == "0" and b0PA and b0AP is False:
            b0AP = b0

        if self.get("phase_enc_dir") == "1" and b0AP and b0PA is False :
            b0PA = b0

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


        self.info("create a suitable mask for the dwi")
        extraArgs = ""
        if self.get("parcellation", "intrasubject"):
            extraArgs += " -usesqform"
	print "b0Image before = ", b0Image
	print "norm before = ", norm
	print "parcellationMask before = ", parcellationMask
	print "target name before = ", self.buildName(parcellationMask, 'resample')

        mask = mriutil.computeDwiMaskFromFreesurfer(b0Image,
                                                    norm,
                                                    parcellationMask,
                                                    self.buildName(parcellationMask, 'resample'),
                                                    extraArgs)

        print "mask name after = ", mask

        #create the acquisition parameter file for eddy
        acqpEddy = self.__createAcquisitionParameterFile('eddy')

        #create an index file
        indexFile = self.__createIndexFile(mriutil.getNbDirectionsFromDWI(dwi))

        outputEddyImage = self.__correctionEddy2(dwi,
                                    mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)

        eddyParameterFiles = self.getImage(self.workingDir, 'dwi', None, 'eddy_parameters')
        if eddyParameterFiles:
            self.info("Apply eddy movement correction to gradient encodings directions")
            bCorrected = mriutil.applyGradientCorrection(bEnc, eddyParameterFiles, self.buildName(outputEddyImage, None, 'b'))
            self.info(mriutil.mrtrixToFslEncoding(outputEddyImage,
                                        bCorrected,
                                        self.buildName(outputEddyImage, None, 'bvecs'),
                                        self.buildName(outputEddyImage, None, 'bvals')))


        #@TODO @BUGS apply eddy correction to the mask

        #QA
        dwi = self.getImage(self.dependDir, 'dwi')
        workingDirDwi = self.getImage(self.workingDir, 'dwi', 'eddy')
        eddyParameterFiles = self.getImage(self.workingDir, 'dwi', ext='eddy_parameters')
        bVecs = self.getImage(self.dependDir, 'grad',  None, 'bvecs')
        bVecsCorrected = self.getImage(self.workingDir, 'grad',  'eddy', 'bvecs')

        dwiCompareGif = self.buildName(workingDirDwi, 'compare', 'gif')
        dwiGif = self.buildName(workingDirDwi, None, 'gif')
        translationsPng = self.buildName(workingDirDwi, 'translations', 'png')
        rotationPng = self.buildName(workingDirDwi, 'rotations', 'png')
        bVecsGif = self.buildName(workingDirDwi, 'vectors', 'gif')

        self.slicerGifCompare(dwi, workingDirDwi, dwiCompareGif, boundaries=mask)
        self.slicerGif(workingDirDwi, dwiGif, boundaries=mask)
        self.slicerGif(workingDirDwi, dwiGif, boundaries=mask)

        self.plotMovement(eddyParameterFiles, translationsPng, rotationPng)
        self.plotvectors(bVecs, bVecsCorrected, bVecsGif)
        

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


    def __bet(self, source):

        self.info("Launch brain extraction from fsl")
        tmp = self.buildName(source, "tmp")
        target = self.buildName(source, "brain")

        cmd = "bet {} {} -m".format(source, tmp)
        self.launchCommand(cmd)
        self.rename(tmp, target)

        self.info("Finish brain extraction from fsl")
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



    def isIgnore(self):
        return self.get("ignore")

    def meetRequirement(self):

        images = Images((self.getImage(self.dependDir, 'dwi'), 'diffusion weighted'),
                        (self.getImage(self.parcellationDir, 'norm'), 'freesurfer normalize'),
                        (self.getImage(self.parcellationDir, 'mask'), 'freesurfer mask'),
                        (self.getImage(self.dependDir, 'grad', None, 'bvals'), 'gradient .bvals encoding file'),
                        (self.getImage(self.dependDir, 'grad', None, 'bvecs'), 'gradient .bvecs encoding file'),
                        (self.getImage(self.dependDir, 'grad', None, 'b'), 'gradient .b encoding file'))
        return images.isAllImagesExists()


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, 'dwi', 'eddy'), 'diffusion weighted eddy corrected'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'bvals'), 'gradient .bvals encoding file'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'bvecs'), 'gradient .bvecs encoding file'),
                  (self.getImage(self.workingDir, 'grad', 'eddy', 'b'), 'gradient .b encoding file'),
                  (self.getImage(self.workingDir, 'mask', 'resample'), 'dwi space mask'))
        return images.isSomeImagesMissing()


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task
        """
        eddyGif = self.getImage(self.workingDir, 'dwi', 'eddy', ext='gif')
        compareGif = self.getImage(self.workingDir, 'dwi', 'compare', ext='gif')
        translationsPng = self.getImage(self.workingDir, 'dwi', 'translations', ext='png')
        rotationsPng = self.getImage(self.workingDir, 'dwi', 'rotations', ext='png')
        bvecsGif = self.getImage(self.workingDir, 'dwi', 'vectors', ext='gif')

        images = Images((eddyGif,'DWI eddy corrected'),
                        (compareGif, 'Before and after eddy corrections'),
                        (translationsPng,'Translation correction by eddy'),
                        (rotationsPng,'Rotation correction by eddy'),
                        (bvecsGif,'Gradients vectors on the unitary sphere. Red : raw bvec | Blue : opposite bvec | Black + : movement corrected bvec'),
                       )
        return images

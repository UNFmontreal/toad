from lib.generictask import GenericTask
from lib import util, mriutil
import glob
import os

__author__ = 'desmat'


class Eddy(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi')
        b0AP= self.getImage(self.dependDir, 'b0AP')
        b0PA= self.getImage(self.dependDir, 'b0PA')
        bFile=  self.getImage(self.dependDir, 'grad',  None, 'b')
        bVals=  self.getImage(self.dependDir, 'grad',  None, 'bval')
        bVecs=  self.getImage(self.dependDir, 'grad',  None, 'bvec')

        #extract b0 image from the dwi
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals))

        #make sure all the images have the same voxel size and dimension scale between them
        self.__validateSizeAndDimension([dwi, b0, b0AP, b0PA])

        #Generate a missing b0 image if we could. --> 0 = P>>A, 1 = A>>P
        if self.get("phase_enc_dir") == "0" and b0PA and b0AP is False:
            b0AP = b0

        if self.get("phase_enc_dir") == "1" and b0AP and b0PA is False :
            b0PA = b0

        [dwi, b0, b0AP, b0PA] = self.__oddImagesWithEvenNumberOfSlices([dwi, b0, b0AP, b0PA])

        if b0AP is False or b0PA is False:
            topupBaseName = None
            mask = self.__bet(b0)

        else:

            #concatenate B0 image together
            b0Image = self.__concatenateB0(b0PA, b0AP,
                            os.path.join(self.workingDir, self.get('b0s_filename')))

            #create the acquisition parameter file
            acqpTopup = self.__createAcquisitionParameterFile('topup')

            #Lauch topup on concatenate B0 image
            [topupBaseName, topupImage] = self.__topup(b0Image, acqpTopup, self.get('b02b0_filename'))
            meanTopup = self.__fslmathsTmean(os.path.join(self.workingDir, topupImage))
            mask = self.__bet(meanTopup)


        #create the acquisition parameter file for eddy
        acqpEddy = self.__createAcquisitionParameterFile('eddy')

        #create an index file
        indexFile = self.__createIndexFile(mriutil.getNbDirectionsFromDWI(dwi))

        outputEddyImage = self.__correctionEddy2(dwi,
                                    mask, topupBaseName, indexFile, acqpEddy, bVecs, bVals)

        #@TODO remove the glob and use getimage
        eddyParameterFiles = glob.glob("{}/*.eddy_parameters".format(self.workingDir))
        if len(eddyParameterFiles)>0:
            bCorrected = mriutil.applyGradientCorrection(bFile, eddyParameterFiles.pop(0), self.workingDir)
            #produce the bVal and bVec file accordingly
            mriutil.bEnc2BVec(bCorrected, self.workingDir)
            mriutil.bEnc2BVal(bCorrected, self.workingDir)


    def  __oddImagesWithEvenNumberOfSlices(self, sources):
        """return a list of images that will count a odd number of slices in z direction

            If an even number of slices is found, the upper volume will be remove

        Args:
            sources: a list of images

        Returns:
             the same list but with images modified

        """
        for i, source in enumerate(sources):
            if source:
                zDims = int(mriutil.getMriDimensions(source)[2])
                if zDims%2 == 1:
                    sources[i]= self.__extractZVolumes(source, "0:{}".format(zDims-2))
        return sources


    def __extractZVolumes(self, source, volumes):
        """Extract a volume along the Z axes

        Args:
            source: The input image
            volumes:  The volume number

        Returns:
             The name of the resulting image
        """

        tmp =  self.buildName(source, "tmp")
        target = self.buildName(source, "subset")
        cmd = "mrconvert {} {} -coord +2 {} -nthreads {} -quiet".format(source, tmp, volumes, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        return self.rename(tmp, target)


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
            text = "0 -1 0 {}\n0 1 0 {}\n".format(factor, factor)

        elif type=='eddy':
            parameter='acqp_eddy'
            if phaseEncDir==0:    #P>>A
                    text = "0 1 0 {}\n".format(factor)
            elif phaseEncDir==1:  #A>>P
                    text = "0 -1 0 {}\n".format(factor)
            elif phaseEncDir==2:  #R>>L
                    text = "1 0 0 {}\n".format(factor)
            elif phaseEncDir==3:  #L>>R
                    text = "-1 0 0 {}\n".format(factor)
            else:
                self.error("Cannot determine the phase encoding direction, got value of: {}".format(phaseEncDir))
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


    def __validateSizeAndDimension(self, sources):

        names = []
        dims = []
        sizes = []

        for source in sources:
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

        cmd = "topup --imain={} --datain={} --config={} --out={}  --iout={} --verbose"\
              .format(source, acqp, b02b0File, baseName, output)
        self.launchCommand(cmd)
        return [baseName, output]


    def __fslmathsTmean(self, source):

        target = source.replace(".nii", "_tmean.nii")
        mriutil.fslmaths(source, target , 'Tmean')
        return target


    def __bet(self, source):

        self.info("Launch brain extraction from fsl")
        tmp = self.buildName(source, "tmp", "nii.gz")
        target = self.buildName(source, "brain")

        cmd = "bet {} {} -v -m".format(source, tmp)
        self.launchCommand(cmd)
        self.rename(tmp, target)

        self.info("Finish brain extraction from fsl")
        return target


    def __correctionEddy2(self, source, mask, topup, index, acqp, bVecs, bVal):
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
              .format(source, mask, index, acqp, bVecs, bVal, tmp)

        if topup is not None:
            cmd += " --topup={}".format(topup)

        self.getNTreadsEddy()
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def isIgnore(self):
        return self.get("ignore") is "True"


    def meetRequirement(self):

        images = {'diffusion weighted':self.getImage(self.dependDir, 'dwi'),
                  'gradient .bval encoding file': self.getImage(self.dependDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.dependDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.dependDir, 'grad', None, 'b')}
        return self.isAllImagesExists(images)


    def isDirty(self):
        images = {'diffusion weighted eddy corrected': self.getImage(self.workingDir, 'dwi', 'eddy'),
                  'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', 'eddy', 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', 'eddy', 'bvec'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', 'eddy', 'b')}
        print "EDDY EDDU DURR"
        print images
        ipeqwruioeru
        return self.isSomeImagesMissing(images)

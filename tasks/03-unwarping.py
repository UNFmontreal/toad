from generic.generictask import GenericTask
from modules import util, mriutil
import glob
import os

__author__ = 'desmat'


class Unwarping(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')


    def implement(self):

        dwi   = self.getImage(self.dependDir, 'dwi')
        b0PA  = self.getImage(self.dependDir, 'b0PA')
        b0AP  = self.getImage(self.dependDir, 'b0AP')
        bFile =  self.getImage(self.dependDir, 'grad',  None, 'b')
        bVals =  self.getImage(self.dependDir, 'grad',  None, 'bval')
        bVecs =  self.getImage(self.dependDir, 'grad',  None, 'bvec')

        #make sure the 3 images have the same voxel size and dimension scale
        self.__validateSizeAndDimension(dwi, b0PA, b0AP)

        #make sure that the z dimension contain an odd number of slices
        dwiZDims = int(mriutil.getMriDimensions(dwi)[2])

        if dwiZDims%2 == 1:
            dwi  = self.__extractZVolumes(dwi, "0:{}".format(dwiZDims-2))
            b0PA = self.__extractZVolumes(b0PA, "0:{}".format(dwiZDims-2))
            b0AP = self.__extractZVolumes(b0AP, "0:{}".format(dwiZDims-2))

        #concatenate B0 image together
        b0Image = self.__concatenateB0(b0PA, b0AP,
                            os.path.join(self.workingDir, self.get('b0s_filename')))

        #create an empty b02b0.cnf file
        #b02b0File = os.path.join(self.workingDir, self.get('b02b0_filename'))
        #open(b02b0File, 'a').close()

        #create the acquisition parameter file
        acqpTopup = self.__createAcquisitionParameterFile('topup')
        acqpEddy = self.__createAcquisitionParameterFile('eddy')

        #create an index file
        indexFile = self.__createIndexFile(mriutil.getNbDirectionsFromDWI(dwi))

        #Lauch topup on concatenate B0 image
        [topupBaseName, topupImage] = self.__topup(b0Image, acqpTopup, self.get('b02b0_filename'))

        outputFieldMask = self.__fslmaths_tmean(os.path.join(self.workingDir, topupImage))

        outputFieldMaskExtracted = self.__bet(outputFieldMask)

        outputEddyImage = self.__correction_eddy2(dwi,
                                    outputFieldMaskExtracted, topupBaseName, indexFile, acqpEddy, bVecs, bVals)

        self.info("Uncompressing eddy output image: {}".format(outputEddyImage))
        util.gunzip(outputEddyImage)

        #@TODO remove the glob and use getimage
        eddyParameterFiles = glob.glob("{}/*.eddy_parameters".format(self.workingDir))
        if len(eddyParameterFiles)>0:
            bCorrected = mriutil.applyGradientCorrection(bFile, eddyParameterFiles.pop(0), self.workingDir)
            #produce the bVal and bVec file accordingly
            mriutil.bEnc2BVec(bCorrected, self.workingDir)
            mriutil.bEnc2BVal(bCorrected, self.workingDir)


    def __extractZVolumes(self, source, volumes):
        """Extract a volume along the Z axes

        Args:
            source: The input image
            volumes:  The volume number

        Returns:
             The name of the resulting image
        """

        tmp = os.path.join(self.workingDir, "tmp.nii")
        target = self.getTarget(source, "subset")
        cmd = "mrconvert {} {} -coord +2 {} -nthreads {} -quiet".format(source, tmp, volumes, self.getNTreadsMrtrix())
        self.launchCommand(cmd)
        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)
        return target


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

        For topup, the image is always concatenate b0AP first then b0PA
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


    def __validateSizeAndDimension(self, dwi, b0PA, b0AP):

        dwiDim   = mriutil.getMriDimensions(dwi)
        dwiVoxel = mriutil.getMriVoxelSize(dwi)
        b0PADim   = mriutil.getMriDimensions(b0PA)
        b0PAVoxel = mriutil.getMriVoxelSize(b0PA)
        b0APDim   = mriutil.getMriDimensions(b0AP)
        b0APVoxel = mriutil.getMriVoxelSize(b0AP)

        self.info("Look if {} and {} and {} have the same voxel size".format(dwi, b0PA, b0AP))
        if len(dwiVoxel) == len(b0PAVoxel) == len(b0APVoxel) == 3:
            for i in range(0,len(dwiVoxel)):
                if not (dwiVoxel[i] == b0PAVoxel[i] == b0APVoxel[i]):
                    self.error("Voxel size mismatch found at index {} for image {} {} {}".format(i, dwi, b0PA, b0AP))
        else:
            self.error("Found Voxel size inconsistency for image {} or  {} or {}".format(dwi, b0PA, b0AP))

        self.info("Look if {} and {} and {} have the same dimension for each scale".format(dwi, b0PA, b0AP))
        for i in range(0,3):
                if not (dwiDim[i]==b0PADim[i]==b0APDim[i]):
                    self.error("Dimensions mismatch found at index {} for image {} {} {}".format(i, dwi, b0PA, b0AP))


    def __topup(self, source, acqp, b02b0File):

        self.info("Launch topup from fsl.\n")
        baseName = os.path.join(self.workingDir, self.get( 'topup_results_base_name'))
        output = os.path.join(self.workingDir, self.get( 'topup_results_output'))

        cmd = "topup --imain={} --datain={} --config={} --out={}  --iout={} --verbose"\
              .format(source, acqp, b02b0File, baseName, output)
        self.launchCommand(cmd)
        return [baseName, output]


    def __fslmaths_tmean(self, source):

        target = source.replace(".nii", "_tmean.nii")
        mriutil.fslmaths(source, target , 'Tmean')
        return target


    def __bet(self, source):

        self.info("Launch brain extraction from fsl")
        tmp = self.getTarget(source, "tmp", "nii.gz")
        target = self.getTarget(source, "brain")

        cmd = "bet {} {} -v -m".format(source, tmp)
        self.launchCommand(cmd)

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        self.info("Finish brain extraction from fsl")
        return target


    def __correction_eddy2(self, source, mask, topup, index, acqp, bVecs, bVal):
        """

        """
        self.info("Launch eddy correction from fsl")
        tmp = self.getTarget(source, "tmp")
        target = self.getTarget(source, "unwarp")
        cmd = "eddy --imain={} --mask={}--topup={} --index={} --acqp={} --bvecs={} --bvals={} --out={} --verbose"\
              .format(source, mask, topup, index, acqp, bVecs, bVal, tmp)

        self.getNTreadsEddy()
        self.launchCommand(cmd)

        self.info(util.gunzip(tmp))

        self.info("renaming {} to {}".format(tmp, target))
        os.rename(tmp, target)

        self.info("Finish eddy correction from fsl")
        return target


    def isIgnore(self):
        return self.isSomeImagesMissing({'posterior to anterior':self.getImage(self.dependDir, 'b0PA'), 'anterior to posterior':self.getImage(self.dependDir, 'b0AP')})


    def meetRequirement(self):

        images = {'diffusion weighted':self.getImage(self.dependDir, 'dwi'),
                  'posterior to anterior':self.getImage(self.dependDir, 'b0PA'),
                  'anterior to posterior':self.getImage(self.dependDir, 'b0PA'),
                  'gradient .bval encoding file': self.getImage(self.dependDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.dependDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.dependDir, 'grad', None, 'b')}

        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {'diffusion weighted unwarped': self.getImage(self.workingDir, 'dwi', 'unwarp'),
                  'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b')}

        return self.isSomeImagesMissing(images)

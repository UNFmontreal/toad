from lib.generictask import GenericTask
from lib import util, mriutil
import glob
import os

__author__ = 'desmat'

class Preprocessing(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'denoising', 'preparation', 'parcellation', 'eddy', 'fieldmap')


    def implement(self):

        dwi = self.__linkDwiImage()

        bFile= self.getImage(self.preparationDir, 'grad', None, 'b')
        if not bFile:
            bFile= self.getImage(self.eddyDir, 'grad', None, 'b')
        bVal= self.getImage(self.preparationDir, 'grad', None, 'bval')
        if not bVal:
            bVal= self.getImage(self.eddyDir, 'grad', None, 'bval')
        bVec= self.getImage(self.eddyDir, 'grad', None, 'bvec')
        if not bVec:
            bVec= self.getImage(self.preparationDir, 'grad', None, 'bvec')

        bFile = util.symlink(bFile, self.workingDir)
        bVal = util.symlink(bVal, self.workingDir)
        bVec = util.symlink(bVec, self.workingDir)

        dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
        b0Upsample = os.path.join(self.workingDir, os.path.basename(dwiUpsample).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwiUpsample, b0Upsample, bVal))

        dwi2x2X2 = self.__upsampling(dwi, "2 2 2", self.buildName(dwi, "2x2x2"))
        b02x2x2 = os.path.join(self.workingDir, os.path.basename(dwi2x2X2).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi2x2X2, b02x2x2, bVal))

        anat = self.getImage(self.parcellationDir, 'anat', 'freesurfer')
        brainAnat  = self.__bet(anat)

        brainAnatUncompress = self.uncompressImage(brainAnat)
        whiteMatterAnat = self.__segmentation(brainAnatUncompress)
        util.gzip(brainAnatUncompress)
        util.gzip(whiteMatterAnat)


    def __linkDwiImage(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'denoise')
        if not dwi:
            dwi = self.getImage(self.fieldmapDir, 'dwi', 'unwarp')
        if not dwi:
            dwi = self.getImage(self.eddyDir,'dwi', 'eddy')
        if not dwi:
            dwi = self.getImage(self.preparationDir, 'dwi')
            return util.symlink(dwi, self.workingDir)


    def __upsampling(self, source, voxelSize, target):
        """Upsample an image specify as input

        The upsampling value should be specified into the config.cfg file

        Args:
            source: The input file
            voxelSize: Size of the voxel

        Return:
            The resulting output file name
        """
        self.info("Launch upsampling from freesurfer.\n")
	tmp = self.buildName(source, "tmp")
        if len(voxelSize.strip().split(" "))!=3:
            self.warning("Voxel size not specified correctly during upsampling")

        cmd = "mri_convert -voxsize {} --input_volume {} --output_volume {}".format(voxelSize, source, tmp)
        self.launchCommand(cmd)
        return self.rename(tmp, target)


    def __bet(self, source):
        """deletes non-brain tissue from an image of the whole head

        bias field & neck cleanup will always be perform by this method

        Args:
            source: The input file name

        Return:
            The resulting output file name
        """
        self.info("Launch brain extraction from fsl")
        target = self.buildName(source, "brain")
        fractionalIntensity =  self.get('fractional_intensity')
        verticalGradient =  self.get('vertical_gradient')

        self.info("End brain extraction from fsl")

        cmd = "bet {} {} -f {} -g {} -v ".format(source, target, fractionalIntensity, verticalGradient)
        if self.getBoolean('reduce_bias'):
            cmd += "-B "
        self.launchCommand(cmd)
        self.info(util.gunzip("{}.gz".format(target)))
        return target


    def __segmentation(self, source):
        """segment an images into different tissue classes

        Segment grey matter, white matter and csf using a modified Gaussian Mixture Model

        Args:
            source: the input T1 image

        Returns:
            the white matter segmented image name
        """
        self.info("Launch segmentation from spm")
        options = util.arrayOfInteger(self.get('segmentation_type'))

        if len(options) != 9:
            self.info("Found {} values into segmentation output_type. Expected 9".format(len(options)))

        if options[8] != 1:
            self.error("White matter map should be produce as a requirement, the third element must be set to 1")

        scriptName = self.__createSegmentationScript(source, options)
        self.launchMatlabCommand(scriptName)
        fileBasename = self.buildName(source, None, "", False)
        dict = {'c1':'gw','c2':'wm','c3':'csf',
                'wc1':'wgw','wc2':'wwm','wc3':'wcsf',
                'mwc1':'mwgw','mwc2':'mwwm','mwc3':'mwcsf'}

        for key, value in dict.items():
            for resultFile in glob.glob("{}/{}{}*.nii".format(self.workingDir,key ,fileBasename)):
                self.rename(resultFile, "{}/{}_{}.nii".format(self.workingDir ,fileBasename, value))

        if (self.getBoolean("cleanup")):
            self.info("Cleaning up extra files")
            postfixs = ["m{}.nii".format(fileBasename), '_seg_sn.mat', '_seg_inv_sn.mat']
            for postfix in postfixs:
                if os.path.exists(os.path.join(self.workingDir, postfix)):
                    os.remove(os.path.join(self.workingDir, postfix))
        
        target = self.buildName(source, "wm")
        if not os.path.exists(target):
            self.error("No white matter image found to return")

        self.info("End Segmentation from spm")
        return target


    def __createSegmentationScript(self, source, options):
        """Create a file which contains all necessary instruction to launch a segmentation with spm

        Args:
            source: the input image file name
            options: an array of nine integer elements representing Boolean. See config.cfg for the meaning of the elements

        Returns:
            The resulting script file name
        """

        scriptName = self.buildName(source, None, ".m")
        self.info("Creating spm segmentation script {}".format(scriptName))

        tags={ 'source': source,
               'gm1': options[0], 'gm2': options[1], 'gm3': options[2],
               'csf1': options[3], 'csf2': options[4], 'csf3': options[5],
               'wm1': options[6], 'wm2': options[7], 'wm3': options[8]}


        template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/segment.tpl"))
        util.createScript(scriptName, template)

        return scriptName


    def meetRequirement(self, result=True):
        #@TODO add gradient files validation and correct this function
        if self.isSomeImagesMissing({'denoised': self.getImage(self.dependDir, "dwi", 'denoise')}):
            dwi = self.getImage(self.eddyDir, "dwi", 'eddy')
            if self.isSomeImagesMissing({'eddy corrected': dwi}):
                dwi = self.getImage(self.preparationDir, "dwi")
                if self.isSomeImagesMissing({'diffusion weighted': dwi}):
                    result=False
                else:
                    self.info("Will take {} image instead".format(dwi))

        images = {'freesurfer high resolution': self.getImage(self.parcellationDir, 'anat', 'freesurfer')}
        result = self.isAllImagesExists(images)
        return result


    def isDirty(self, result = False):

        images = {'upsampled diffusion weighted': self.getImage(self.workingDir, 'dwi', "upsample"),
                    '2x2x2 diffusion weighted': self.getImage(self.workingDir, 'dwi', "2x2x2"),
                    'upsampled b0': self.getImage(self.workingDir, 'b0', "upsample"),
                    '2x2x2 b0': self.getImage(self.workingDir, 'b0', "2x2x2"),
                    'high resolution brain extracted': self.getImage(self.workingDir, 'anat', "brain"),
                    'high resolution white matter brain extracted': self.getImage(self.workingDir, 'anat', ["brain", "wm"])}
        return self.isSomeImagesMissing(images)


    def qaSupplier(self):

        b0Upsampled = self.getImage(self.workingDir, 'b0', "upsample")

        #@DEBUG
        self.info("Produce {} image".format(b0Upsampled))
        anatBrain = self.getImage(self.workingDir ,'anat', "brain")
        anatBrainWhiteMatter = self.getImage(self.workingDir ,'anat',["brain", "wm"])

        self.pngSlicerImage(b0Upsampled, anatBrain)
        self.pngSlicerImage(b0Upsampled, anatBrainWhiteMatter)

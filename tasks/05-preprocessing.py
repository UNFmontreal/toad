from lib.generictask import GenericTask
from lib import util, mriutil
import glob
import os

__author__ = 'desmat'

class Preprocessing(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'denoising', 'preparation', 'eddy')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi', 'denoise')
        if not dwi:
            dwi = self.getImage(self.eddyDir, 'dwi', 'eddy')
            if not dwi:
                dwi = self.getImage(self.dependDir, 'dwi')

        bVal= self.getImage(self.eddyDir, 'grad', None, 'bval')
        if not bVal:
            bVal= self.getImage(self.preparationDir, 'grad', None, 'b')


        dwiUpsample=  self.__upsampling(dwi)
        b0Upsample = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.config.get("prefix", 'dwi'), self.config.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwiUpsample, b0Upsample, bVal))

        #B0 WM segmentation is void
        #whiteMatterDWI = self.__segmentation(b0Upsample)

        anat = self.getImage(self.preparationDir, 'anat')
        brainAnat      = self.__bet(anat)
        whiteMatterAnat= self.__segmentation(brainAnat)


    def __upsampling(self, source):
        """Upsample an image specify as input

        The upsampling value should be specified into the config.cfg file

        Args:
            source: The input file

        Return:
            The resulting output file name
        """
        self.info("Launch upsampling from freesurfer.\n")

        voxelSize = self.get('voxel_size')
        if len(voxelSize.strip().split(" "))!=3:
            self.warning("Voxel size not specified correctly during upsampling")

        target = self.buildName(source, "upsample")
        cmd = "mri_convert -voxsize {} --input_volume {} --output_volume {}".format(voxelSize, source, target)
        self.launchCommand(cmd)
        return target


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

        scriptName = os.path.join(self.workingDir, os.path.basename(source).replace(".nii",".m"))
        self.info("Creating spm segmentation script {}".format(scriptName))

        tags={ 'source': source,
               'gm1': options[0], 'gm2': options[1], 'gm3': options[2],
               'csf1': options[3], 'csf2': options[4], 'csf3': options[5],
               'wm1': options[6], 'wm2': options[7], 'wm3': options[8]}

        template = self.parseTemplate(tags, os.path.join(self.toadDir, "templates/files/segment.tpl"))
        util.createScript(scriptName, template)

        return scriptName


    def meetRequirement(self, result=True):

        if self.isSomeImagesMissing({'denoised': self.getImage(self.dependDir, "dwi", 'denoise')}):
            dwi = self.getImage(self.eddyDir, "dwi", 'eddy')
            if self.isSomeImagesMissing({'eddy corrected': dwi}):
                dwi = self.getImage(self.preparationDir, "dwi")
                if self.isSomeImagesMissing({'diffusion weighted': dwi}):
                    result=False
                else:
                    self.info("Will take {} image instead".format(dwi))

        images = {'high resolution': self.getImage(self.preparationDir, 'anat')}
        result = self.isAllImagesExists(images)
        return result


    def isDirty(self, result = False):

        images = {'upsampled diffusion weighted': self.getImage(self.workingDir ,'dwi', "upsample"),
                    'high resolution brain extracted': self.getImage(self.workingDir ,'anat', "brain"),
                    'high resolution white matter': self.getImage(self.workingDir ,'anat', "wm"),
                    'b0 white matter': self.getImage(self.workingDir ,'b0', "wm")}
        return self.isSomeImagesMissing(images)

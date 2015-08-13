import glob
import os

from core.generictask import GenericTask
from lib import util, mriutil
from lib.images import Images

__author__ = 'desmat'

class Upsampling(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'denoising', 'preparation', 'parcellation', 'eddy', 'fieldmap', 'qa')


    def implement(self):

        dwi = self.__linkDwiImage()

        bVals= self.getImage(self.eddyDir, 'grad', None, 'bvals')
        bVecs= self.getImage(self.eddyDir, 'grad', None, 'bvecs')
	bEnc = self.getImage(self.eddyDir, 'grad', None, 'benc')
        if not bVals or not bVecs:
            bVals= self.getImage(self.preparationDir, 'grad', None, 'bvals')
            bVecs= self.getImage(self.preparationDir, 'grad', None, 'bvecs')
            bEnc= self.getImage(self.preparationDir, 'grad', None, 'benc')
        bVals = util.symlink(bVals, self.workingDir)
        bVecs = util.symlink(bVecs, self.workingDir)
	bEnc = util.symlink(bEnc, self.workingDir)

        dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
        b0Upsample = os.path.join(self.workingDir, os.path.basename(dwiUpsample).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwiUpsample, b0Upsample, bVals))


        #QA
        """
        anat = self.getImage(self.parcellationDir, 'anat', 'freesurfer')
        anatBrainMask = self.getImage(self.workingDir, 'anat', ['brain', 'mask'])
        anatWmMask = self.getImage(self.workingDir, 'anat', ['brain', 'wm'])

        anatBrainMaskPng = self.buildName(anatBrainMask, None, 'png')
        anatWmMaskPng = self.buildName(anatWmMask, None, 'png')

        self.slicerPng(anat, anatBrainMaskPng, maskOverlay=anatBrainMask, boundaries=anatBrainMask)
        self.slicerPng(anat, anatWmMaskPng, maskOverlay=anatWmMask, boundaries=anatWmMask)
        """

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


    def meetRequirement(self, result=True):

        #@TODO add gradient files validation and correct this function
        images = Images((self.getImage(self.dependDir, "dwi", 'denoise'), 'denoised'),
                       (self.getImage(self.eddyDir, "dwi", 'eddy'), 'eddy corrected'),
                       (self.getImage(self.preparationDir, "dwi"), 'diffusion weighted'))
        if images.isNoImagesExists():
            self.warning("No proper dwi image found as requirement")
            result = False

        images = Images((self.getImage(self.parcellationDir, 'anat', 'freesurfer'), 'freesurfer high resolution'))
        result = images.isAllImagesExists()
        return result


    def isDirty(self):
        images = Images((self.getImage(self.workingDir, 'dwi', "upsample"), 'upsampled diffusion weighted'),
                  (self.getImage(self.workingDir, 'b0', "upsample"), 'upsampled b0'))
        return images.isSomeImagesMissing()

    """
    def qaSupplier(self):

        anatBrainMaskPng = self.getImage(self.workingDir, 'anat', ['brain', 'mask'], ext='png')
        #anatWmMaskPng = self.getImage(self.workingDir, 'anat', ['brain', 'wm'], ext='png')
        #(anatWmMaskPng, 'White matter mask on high resolution anatomical image of freesurfer'),
        return Images((anatBrainMaskPng, 'Brain mask on high resolution anatomical image of freesurfer'))
    """

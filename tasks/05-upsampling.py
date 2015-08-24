import os
from core.generictask import GenericTask
from lib import util, mriutil
from lib.images import Images

__author__ = 'desmat'

class Upsampling(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'denoising', 'preparation', 'parcellation', 'correction')


    def implement(self):

        dwi = self.__linkDwiImage()

        bVals= self.getCorrectionImage('grad', None, 'bvals')
        bVecs= self.getCorrectionImage('grad', None, 'bvecs')
        bEnc = self.getCorrectionImage('grad', None, 'benc')
        if not bVals or not bVecs:
            bVals= self.getPreparationImage('grad', None, 'bvals')
            bVecs= self.getPreparationImage('grad', None, 'bvecs')
            bEnc= self.getPreparationImage('grad', None, 'benc')

        bVals = util.symlink(bVals, self.workingDir)
        bVecs = util.symlink(bVecs, self.workingDir)
        bEnc = util.symlink(bEnc, self.workingDir)

        dwiUpsample= self.__upsampling(dwi, self.get('voxel_size'), self.buildName(dwi, "upsample"))
        b0Upsample = os.path.join(self.workingDir, os.path.basename(dwiUpsample).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwiUpsample, b0Upsample, bVals))


    def __linkDwiImage(self):

        dwi = self.getDenoisingImage('dwi', 'denoise')
        if not dwi:
            dwi = self.getCorrectionImage('dwi', 'corrected')
        if not dwi:
            dwi = self.getPreparationImage('dwi')
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
        images = Images((self.getDenoisingImage("dwi", 'denoise'), 'denoised'),
                       (self.getCorrectionImage("dwi", 'corrected'), 'corrected'),
                       (self.getPreparationImage("dwi"), 'diffusion weighted'))

        if images.isNoImagesExists():
            self.warning("No proper dwi image found as requirement")
            result = False

        return result


    def isDirty(self):
        return Images((self.getImage('dwi', "upsample"), 'upsampled diffusion weighted'),
                  (self.getImage('b0', "upsample"), 'upsampled b0'))

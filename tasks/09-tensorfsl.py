from core.generictask import GenericTask
from lib.images import Images
__author__ = 'desmat'

class TensorFsl(GenericTask):


    def __init__(self, subject):
        """Fits a diffusion tensor model at each voxel
        """
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):
        """Placeholder for the business logic implementation

        """

        dwi = self.getImage(self.dependDir,'dwi','upsample')
        bVals = self.getImage(self.dependDir, 'grad', None, 'bvals')
        bVecs = self.getImage(self.dependDir, 'grad', None, 'bvecs')
        mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])

        self.__produceTensors(dwi, bVecs, bVals, mask)

        l1 = self.getImage(self.workingDir, 'dwi', 'fsl_l1')
        l2 = self.getImage(self.workingDir, 'dwi', 'fsl_l2')
        l3 = self.getImage(self.workingDir, 'dwi', 'fsl_l3')

        ad = self.buildName(dwi, 'fsl_ad')
        rd = self.buildName(dwi, 'fsl_rd')

        self.rename(l1, ad)
        self.__mean(l2, l3, rd)


    def __produceTensors(self, source, bVecs, bVals, mask=""):
        """Fits a diffusion tensor model at each voxel

        Args:
            source: A diffusion weighted volumes and volume(s) with no diffusion weighting
            bVecs: Text file containing a list of gradient directions applied during diffusion weighted volumes.
            bVals: Text file containing a list of b values applied during each volume acquisition.
            mask: A binarised volume in diffusion space containing ones inside the brain and zeroes outside the brain.

        """
        self.info("Starting dtifit from fsl")
        target = self.buildName(source, None,  '')
        cmd ="dtifit -k {} -o {} -r {} -b {} --save_tensor --sse ".format(source, target, bVecs, bVals)
        if mask:
            cmd += "-m {}".format(mask)
        self.launchCommand(cmd)


    def __mean(self, source1, source2, target):
        cmd = "fslmaths {} -add {} -div 2 {}".format(source1, source2, target)
        self.launchCommand(cmd)


    def __createMask(self, source):
        """deletes non-brain tissue from an image of the whole head

        bias field & neck cleanup will always be perform by this method

        Args:
            source: The input file name

        Return:
            The resulting output file name
        """
        self.info("Launch brain extraction from fsl")
        target = self.buildName(source, "brain")
        fractionalIntensity = 0.4
        verticalGradient = 0
        self.info("End brain extraction from fsl")
        cmd = "bet {} {} -f {} -g {} -m".format(source, target, fractionalIntensity, verticalGradient)
        self.launchCommand(cmd)

        return target


    def meetRequirement(self, result=True):
        """Validate if all requirements have been met prior to launch the task

        """
        images = Images((self.getImage(self.dependDir,'dwi','upsample'), 'diffusion weighted'),
                  (self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask']), 'ultimate mask'),
                  (self.getImage(self.dependDir, 'grad', None, 'bvals'), '.bvals gradient encoding file'),
                  (self.getImage(self.dependDir, 'grad', None, 'bvecs'), '.bvecs gradient encoding file'))

        return images.isAllImagesExists()


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        images = Images((self.getImage(self.workingDir, 'dwi', 'fsl_v1'), "1st eigenvector"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_v2'), "2rd eigenvector"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_v3'), "3rd eigenvector"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_ad'), "selected eigenvalue(s) AD"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_rd'), "selected eigenvalue(s) RD"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_md'), "mean diffusivity"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_fa'), "fractional anisotropy"),
                      (self.getImage(self.workingDir, 'dwi', 'fsl_so'), "raw T2 signal with no weighting"))

        return images.isSomeImagesMissing()

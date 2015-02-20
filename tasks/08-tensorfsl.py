from lib.generictask import GenericTask
from lib import mriutil
import os

__author__ = 'desmat'

class TensorFsl(GenericTask):


    def __init__(self, subject):
        """Fits a diffusion tensor model at each voxel
        """
        GenericTask.__init__(self, subject, 'preprocessing', 'masking')


    def implement(self):
        """Placeholder for the business logic implementation

        """
        dwi = self.getImage(self.dependDir, 'dwi', '2x2x2')
        bVal = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVec = self.getImage(self.dependDir, 'grad', None, 'bvec')
        mask = self.getImage(self.maskingDir, 'anat', ['2x2x2', 'extended', 'mask'])

        self.__tensorsFsl(dwi, bVec, bVal, mask)

        l1 = self.getImage(self.workingDir, 'dwi', 'fsl_l1')
        l2 = self.getImage(self.workingDir, 'dwi', 'fsl_l2')
        l3 = self.getImage(self.workingDir, 'dwi', 'fsl_l3')

        ad = self.buildName(dwi, 'fsl_ad')
        rd = self.buildName(dwi, 'fsl_rd')

        self.rename(l1, ad)
        self.__mean(l2, l3, rd)


    def __tensorsFsl(self, source, bVec, bVal, mask=""):
        """Fits a diffusion tensor model at each voxel

        Args:
            source: A diffusion weighted volumes and volume(s) with no diffusion weighting
            bVec: Text file containing a list of gradient directions applied during diffusion weighted volumes.
            bVal: Text file containing a list of b values applied during each volume acquisition.
            mask: A binarised volume in diffusion space containing ones inside the brain and zeroes outside the brain.

        """
        self.info("Starting dtifit from fsl")
        target = self.buildName(source, 'tensor', '')
        cmd ="dtifit -k {} -o {} -r {} -b {} --save_tensor --sse ".format(source, target, bVec, bVal)
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
        cmd = "bet {} {} -f {} -g {} -v -m".format(source, target, fractionalIntensity, verticalGradient)
        self.launchCommand(cmd)

        return target


    def meetRequirement(self, result=True):
        """Validate if all requirements have been met prior to launch the task

        """
        images = {'diffusion weighted':  self.getImage(self.dependDir, 'dwi', '2x2x2'),
                  'ultimate 2x2x2 mask': self.getImage(self.maskingDir, 'anat', ['2x2x2', 'extended', 'mask']),
                  '.bval gradient encoding file': self.getImage(self.dependDir, 'grad', None, 'bval'),
                  '.bvec gradient encoding file': self.getImage(self.dependDir, 'grad', None, 'bvec'),
                }

        return self.isAllImagesExists(images)


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        images = {"1st eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_v1'),
                  "2rd eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_v2'),
                  "3rd eigenvector": self.getImage(self.workingDir, 'dwi', 'fsl_v3'),
                  "selected eigenvalue(s) AD": self.getImage(self.workingDir, 'dwi', 'fsl_ad'),
                  "selected eigenvalue(s) RD": self.getImage(self.workingDir, 'dwi', 'fsl_rd'),
                  "mean diffusivity": self.getImage(self.workingDir, 'dwi', 'fsl_md'),
                  "fractional anisotropy": self.getImage(self.workingDir, 'dwi', 'fsl_fa'),
                  "raw T2 signal with no weighting": self.getImage(self.workingDir, 'dwi', 'fsl_so')}

        return self.isSomeImagesMissing(images)

# -*- coding: utf-8 -*-
import os
import amico

amico.core.setup()

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util
from lib.mriutil import getBValues
import shutil

__author__ = "Mathieu Desrosiers, Arnaud Bore"
__copyright__ = "Copyright (C) 2016, TOAD"
__credits__ = ["Mathieu Desrosiers", "Arnaud Bore"]


class TensorFsl(GenericTask):

    def __init__(self, subject):
        """Fits a diffusion tensor model at each voxel
        """
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'masking', 'qa')

    def implement(self):
        """Placeholder for the business logic implementation

        """

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        bVals = self.getUpsamplingImage('grad', None, 'bvals')
        bVecs = self.getUpsamplingImage('grad', None, 'bvecs')
        bEnc = self.getUpsamplingImage('grad', None, 'b')
        #mask = self.getImage(self.maskingDir, 'anat', ['resample', 'extended', 'mask'])
        mask = self.getRegistrationImage('mask', 'resample')

        if self.get('fitNODDI'):
            kernels = os.path.join(self.subjectDir, 'kernels' )
            if os.path.exists(kernels):
                shutil.rmtree(kernels)
            self.__fitNODDI(dwi, bVals, bVecs, bEnc, mask)
            shutil.rmtree(kernels)

        self.__produceTensors(dwi, bVecs, bVals, mask)

        l1 = self.getImage('dwi', 'l1')
        l2 = self.getImage('dwi', 'l2')
        l3 = self.getImage('dwi', 'l3')

        ad = self.buildName(dwi, 'ad')
        rd = self.buildName(dwi, 'rd')

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

        fitMethod = self.get('fitMethod')  # Fitting method

        cmd = "dtifit -k {} -o {} -r {} -b {} --save_tensor --sse ".format(source, target,
                                                                           bVecs, bVals, fitMethod)

        if fitMethod == 'WLS':
            cmd += ' --wls '

        if mask:
            cmd += "-m {}".format(mask)
        self.launchCommand(cmd)

        fslPostfix = {'fa': 'FA', 'md': 'MD', 'mo': 'MO', 'so': 'S0',
                      'v1': 'V1', 'v2': 'V2', 'v3': 'V3', 'l1': 'L1', 'l2': 'L2', 'l3': 'L3'}
        for postfix, value in fslPostfix.iteritems():
            src = self.buildName(source, value)
            dst = self.buildName(source, postfix)
            self.info("rename {} to {}".format(src, dst))
            os.rename(src, dst)

    def __fitNODDI(self, dwi, bVals, bVecs, bEnc, mask):


        BValues = getBValues(dwi, bEnc)
        # Init amico
        ae = amico.Evaluation(self.subjectDir, self.workingDir.split('/')[-1])
        # Convert bvecs bvals to scheme
        amico.util.fsl2scheme( bVals, bVecs, os.path.join(self.workingDir, "dwi.scheme"), bStep=BValues)
        # Load data
        ae.load_data(dwi_filename = dwi, scheme_filename = "dwi.scheme", mask_filename = mask, b0_thr = 0)
        # Compute noddi model
        ae.set_model("NODDI")
        ae.generate_kernels()
        ae.load_kernels()
        ae.fit()
        # Save File
        ae.save_results()

    def __mean(self, source1, source2, target):
        cmd = "fslmaths {} -add {} -div 2 {}".format(source1, source2, target)
        self.launchCommand(cmd)

    def isIgnore(self):
        return self.get("ignore")

    def meetRequirement(self, result=True):
        """Validate if all requirements have been met prior to launch the task

        """
        return Images((self.getUpsamplingImage('dwi','upsample'), 'diffusion weighted'),
                  (self.getRegistrationImage('mask', 'resample'), 'brain mask'),
                  (self.getUpsamplingImage('grad', None, 'bvals'), '.bvals gradient encoding file'),
                  (self.getUpsamplingImage('grad', None, 'bvecs'), '.bvecs gradient encoding file'))

    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images((self.getImage('dwi', 'v1'), "1st eigenvector"),
                      (self.getImage('dwi', 'v2'), "2rd eigenvector"),
                      (self.getImage('dwi', 'v3'), "3rd eigenvector"),
                      (self.getImage('dwi', 'ad'), "selected eigenvalue(s) AD"),
                      (self.getImage('dwi', 'rd'), "selected eigenvalue(s) RD"),
                      (self.getImage('dwi', 'md'), "mean diffusivity"),
                      (self.getImage('dwi', 'fa'), "fractional anisotropy"),
                      (self.getImage('dwi', 'so'), "raw T2 signal with no weighting"))

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()
        softwareName = 'fsl'

        #Set information
        information = "Fit method: {}".format(self.get('fitMethod'))
        qaImages.setInformation(information)

        #Get images
        mask = self.getRegistrationImage('mask', 'resample')

        #Build qa images
        tags = (
            ('fa', 0.7, 'Fractional anisotropy'),
            ('ad', 0.005, 'Axial Diffusivity'),
            ('md', 0.005, 'Mean Diffusivity'),
            ('rd', 0.005, 'Radial Diffusivity'),
            )

        for postfix, vmax, description in tags:
            image = self.getImage('dwi', postfix)
            if image:
                imageQa = self.plot3dVolume(
                        image, fov=mask, vmax=vmax,
                        colorbar=True, postfix=softwareName)
                qaImages.append((imageQa, description))

        #Build SSE image
        sse = self.getImage('dwi', 'sse')
        sseQa = self.plot3dVolume(
                sse, fov=mask, postfix=softwareName, colorbar=True)
        qaImages.append((sseQa, 'Sum of squared errors'))

        return qaImages

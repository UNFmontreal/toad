# -*- coding: utf-8 -*-
import os

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Preparation(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'backup', 'qa')


    def implement(self):

        dwi = self.getBackupImage('dwi')
        bEncs = self.getBackupImage('grad', None, 'b')
        bVals = self.getBackupImage('grad', None, 'bvals')
        bVecs = self.getBackupImage('grad', None, 'bvecs')


        (bEncs, bVecs, bVals) = self.__produceEncodingFiles(bEncs, bVecs, bVals, dwi)

        expectedLayout = self.get('stride_orientation')
        if not mriutil.isDataStridesOrientationExpected(dwi, expectedLayout) \
                and self.get("force_realign_strides"):

            self.warning("Reorienting strides for image {}".format(dwi))
            self.__stride4DImage(dwi, bEncs, bVecs, bVals, expectedLayout)

        else:
            self.info("Linking {} to {}".format(dwi, util.symlink(dwi, self.workingDir)))

        images = Images((self.getBackupImage('anat'),'high resolution'),
                    (self.getBackupImage('b0_pa'),'B0 posterior to anterior'),
                    (self.getBackupImage('b0_ap'),'B0 anterior to posterior'),
                    (self.getBackupImage('mag'),'MR magnitude'),
                    (self.getBackupImage('phase'),'MR phase '),
                    (self.getBackupImage('aparc_aseg'),'parcellation'),
                    (self.getBackupImage('anat', 'freesurfer'),'freesurfer anatomical'),
                    (self.getBackupImage('lh_ribbon'),'left hemisphere ribbon'),
                    (self.getBackupImage('rh_ribbon'),'right hemisphere ribbon'),
                    (self.getBackupImage('brodmann'),'brodmann'))

        for image, description in images.getData():
            if image:
                if not mriutil.isDataStridesOrientationExpected(image, expectedLayout) \
                        and self.get("force_realign_strides"):
                    self.info(mriutil.stride3DImage(image, self.buildName(image, "stride"), expectedLayout))
                else:
                    self.info("Found {} image, linking {} to {}".format(description, image, util.symlink(image, self.workingDir)))

        for directory in [os.path.join(self.backupDir, directory) for directory in os.listdir(self.backupDir) if os.path.isdir(os.path.join(self.backupDir, directory))]:
            if mriutil.isAfreesurferStructure(directory):
                self.info("{} seem\'s a valid freesurfer structure: linking to {} directory".format(directory, self.workingDir))
                os.symlink(directory, self.get("parcellation", "id"))


    def __produceEncodingFiles(self, bEncs, bVecs, bVals, dwi):

        self.info("Produce .b .bvals and .bvecs gradient file if not existing")
        if not bEncs:
            bEncs = self.buildName(dwi, None, "b")
            self.info(mriutil.fslToMrtrixEncoding(dwi, bVecs, bVals, bEncs))
        else:
            self.info("Linking {} to {}".format(bEncs, util.symlink(bEncs, self.workingDir)))


        if not bVecs or not bVals:

            self.info(mriutil.mrtrixToFslEncoding(dwi,
                                                    bEncs,
                                                    self.buildName(dwi, None, "bvecs"),
                                                    self.buildName(dwi, None, "bvals")))
        else:
            self.info("Linking {} to {}".format(bVecs, util.symlink(bVecs, self.workingDir)))
            self.info("Linking {} to {}".format(bVals, util.symlink(bVals, self.workingDir)))

        return (self.getImage('grad', None, 'b'),
                self.getImage('grad', None, 'bvecs'),
                self.getImage('grad', None, 'bvals'))


    def __stride4DImage(self, source, bEncs, bVecs, bVals, layout="1,2,3"):
        """perform a reorientation of the axes and flip the image into a different layout. stride gredient encoding files
            as well if provided

        Args:
            source:           the input image
            bEncs:            a mrtrix gradient encoding files to stride
            bVecs:            a vector gradient encoding files to stride
            bVals:            a value gradient encoding files to strides
            layout:           comma-separated list that specify the strides.

        Returns:
            the name of the resulting filename
        """
        dwiStride = self.buildName(source, "stride")
        bEncsStride = self.buildName(bEncs, "stride")
        bVecsStride= self.buildName(bVecs, "stride")
        bValsStride= self.buildName(bVals, "stride")

        subCommand = "mrconvert {} {} -quiet -force -stride {},4".format(source, dwiStride, layout)

        cmd = "{} -grad {} -export_grad_mrtrix {} ".format(subCommand, bEncs, bEncsStride)
        self.launchCommand(cmd)

        cmd = "{} -fslgrad {} {} -export_grad_fsl {} {}".format(subCommand, bVecs, bVals, bVecsStride, bValsStride)
        self.launchCommand(cmd)

        return dwiStride, bEncsStride, bVecsStride, bValsStride


    def meetRequirement(self, result=True):

        images = Images((self.getBackupImage('anat'), 'high resolution'),
                  (self.getBackupImage('dwi'), 'diffusion weighted'))

        if images.isSomeImagesMissing():
            result = False

        if not (self.getBackupImage('grad', None, 'b') or
                (self.getBackupImage('grad', None, 'bvals')
                 and self.getBackupImage('grad', None, 'bvecs'))):
            self.error("No gradient encoding file found in {}".format(self.backupDir))
            result = False

        return result


    def isDirty(self):

        return Images((self.getImage('grad', None, 'bvals'), 'gradient .bvals encoding file'),
                      (self.getImage('grad', None, 'bvecs'), 'gradient .bvecs encoding file'),
                      (self.getImage('grad', None, 'b'), 'gradient .b encoding file'),
                      (self.getImage('anat'), 'high resolution'),
                      (self.getImage('dwi'), 'diffusion weighted'))

    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        tags = (
            ('anat', self.plot3dVolume, 'High resolution anatomical image'),
            ('dwi', self.plot4dVolume, 'Diffusion weighted image'),
            ('b0_ap', self.plot3dVolume, 'B0 AP image'),
            ('b0_pa', self.plot3dVolume, 'B0 PA image'),
            ('mag', self.plot3dVolume, 'Magnitude image'),
            ('phase', self.plot3dVolume, 'Phase image'),
            )
        for prefix, plotMethod, description in tags:
            source = self.getImage(prefix)
            if source:
                qaImage = plotMethod(source)
                qaImages.append((qaImage, description))

        return qaImages

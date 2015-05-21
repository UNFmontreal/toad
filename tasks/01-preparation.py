from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil
import os
__author__ = 'desmat'


class Preparation(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'backup', 'qa')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi')
        bEncs = self.getImage(self.dependDir, 'grad', None, 'b')
        bVals = self.getImage(self.dependDir, 'grad', None, 'bvals')
        bVecs = self.getImage(self.dependDir, 'grad', None, 'bvecs')
        (bEncs, bVecs, bVals) = self.__produceEncodingFiles(bEncs, bVecs, bVals, dwi)
        expectedLayout = self.get('stride_orientation')
        if not mriutil.isDataStridesOrientationExpected(dwi, expectedLayout) \
                and self.getBoolean("force_realign_strides"):

            self.warning("Reorienting strides for image {}".format(dwi))
            self.__stride4DImage(dwi, bEncs, bVecs, bVals, expectedLayout)

        else:
            self.info("Linking {} to {}".format(dwi, util.symlink(dwi, self.workingDir)))

        images = Images((self.getImage(self.dependDir, 'anat'),'high resolution'),
                    (self.getImage(self.dependDir, 'b0_pa'),'B0 posterior to anterior'),
                    (self.getImage(self.dependDir, 'b0_ap'),'B0 anterior to posterior'),
                    (self.getImage(self.dependDir, 'mag'),'MR magnitude'),
                    (self.getImage(self.dependDir, 'phase'),'MR phase '),
                    (self.getImage(self.dependDir,'aparc_aseg'),'parcellation'),
                    (self.getImage(self.dependDir, 'anat', 'freesurfer'),'freesurfer anatomical'),
                    (self.getImage(self.dependDir, 'lh_ribbon'),'left hemisphere ribbon'),
                    (self.getImage(self.dependDir, 'rh_ribbon'),'right hemisphere ribbon'),
                    (self.getImage(self.dependDir, 'brodmann'),'brodmann'))

        for image, description in images.getData():
            if image:
                if not mriutil.isDataStridesOrientationExpected(image, expectedLayout) \
                        and self.getBoolean("force_realign_strides"):
                    self.info(mriutil.stride3DImage(image, self.buildName(image, "stride"), expectedLayout))
                else:
                    self.info("Found {} image, linking {} to {}".format(description, image, util.symlink(image, self.workingDir)))

        for directory in [os.path.join(self.dependDir, directory) for directory in os.listdir(self.dependDir) if os.path.isdir(os.path.join(self.dependDir, directory))]:
            if mriutil.isAfreesurferStructure(directory):
                self.info("{} seem\'s a valid freesurfer structure: linking to {} directory".format(directory, self.workingDir))
                os.symlink(directory, self.config.get("parcellation", "id"))


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

        return (self.getImage(self.workingDir, 'grad', None, 'b'),
                self.getImage(self.workingDir, 'grad', None, 'bvecs'),
                self.getImage(self.workingDir, 'grad', None, 'bvals'))


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

        images = Images((self.getImage(self.dependDir, 'anat'), 'high resolution'),
                  (self.getImage(self.dependDir, 'dwi'), 'diffusion weighted'))

        if images.isSomeImagesMissing():
            result = False

        if not (self.getImage(self.dependDir, 'grad', None, 'b') or
                (self.getImage(self.dependDir, 'grad', None, 'bvals')
                 and self.getImage(self.dependDir, 'grad', None, 'bvecs'))):
            self.error("No gradient encoding file found in {}".format(self.dependDir))
            result = False

        return result


    def isDirty(self):

        images = Images((self.getImage(self.workingDir, 'grad', None, 'bvals'), 'gradient .bvals encoding file'),
                      (self.getImage(self.workingDir, 'grad', None, 'bvecs'), 'gradient .bvecs encoding file'),
                      (self.getImage(self.workingDir, 'grad', None, 'b'), 'gradient .b encoding file'),
                      (self.getImage(self.workingDir, 'anat'), 'high resolution'),
                      (self.getImage(self.workingDir, 'dwi'), 'diffusion weighted'))
        return images.isSomeImagesMissing()


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        #Anat and dwi images
        anat = self.getImage(self.workingDir, 'anat')
        anatPng = self.buildName(anat, None, 'png')
        self.slicerPng(anat, anatPng)

        dwi = self.getImage(self.workingDir, 'dwi')
        dwiGif = self.buildName(dwi, None, 'gif')
        self.slicerGif(dwi, dwiGif)

        images = Images((anatPng, 'High resolution anatomical image'),
                        (dwiGif, 'Diffusion weighted image'))

        #AP and PA images
        ap = self.getImage(self.workingDir, 'b0_ap')
        pa = self.getImage(self.workingDir, 'b0_pa')

        if ap:
            apPng = self.buildName(ap, None, 'png')
            self.slicerPng(ap, apPng)
            paPng = self.buildName(pa, None, 'png')
            self.slicerPng(pa, paPng)
            images.extend(Images((apPng, 'B0 AP image'),
                                 (paPng, 'B0 PA image')))

        #Fieldmap
        mag = self.getImage(self.workingDir, 'mag')
        phase = self.getImage(self.workingDir, 'phase')

        if mag:
            magPng = self.buildName(mag, None, 'png')
            self.slicerPng(mag, magPng)
            phasePng = self.buildName(phase, None, 'png')
            self.slicerPng(phase, phasePng)
            images.extend(Images((magPng, 'MR magnitude'),
                                 (phasePng, 'MR phase')))

        return images

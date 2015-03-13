from lib.generictask import GenericTask
from lib import util, mriutil

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
            self.stride4DImage(dwi, bEncs, bVecs, bVals, expectedLayout)

        else:
            util.symlink(dwi, self.workingDir)

        images = {'high resolution': self.getImage(self.dependDir, 'anat'),
                    'B0 posterior to anterior': self.getImage(self.dependDir, 'b0PA'),
                    'B0 anterior to posterior': self.getImage(self.dependDir, 'b0AP'),
                    'MR magnitude ': self.getImage(self.dependDir, 'mag'),
                    'MR phase ': self.getImage(self.dependDir, 'phase'),
                    'parcellation': self.getImage(self.dependDir,'aparc_aseg'),
                    'freesurfer anatomical': self.getImage(self.dependDir, 'anat', 'freesurfer'),
                    'left hemisphere ribbon': self.getImage(self.dependDir, 'lh_ribbon'),
                    'right hemisphere ribbon': self.getImage(self.dependDir, 'rh_ribbon'),
                    'brodmann': self.getImage(self.dependDir, 'brodmann')}

        for key, value in images.iteritems():
            if value:
                if not mriutil.isDataStridesOrientationExpected(value, expectedLayout) \
                        and self.getBoolean("force_realign_strides"):
                    mriutil.stride3DImage(value, self.buildName(value, "stride"), expectedLayout)

                else:
                    self.info("Found {} image, linking file {} to {}".format(key, value, self.workingDir))
                    util.symlink(value, self.workingDir)

    def __produceEncodingFiles(self, bEncs, bVecs, bVals, dwi):

        self.info("Produce .b .bvals and .bvecs gradient file if not existing")
        if not bEncs:
            bEncs = mriutil.fslToMrtrixEncoding(dwi, bVecs, bVals, self.buildName(dwi, None, "b"))
        else:
            util.symlink(bEncs, self.workingDir)

        if not bVecs or not bVals:
            (bVecs, bVals) = mriutil.mrtrixToFslEncoding(dwi,
                                                         bEncs,
                                                         self.buildName(dwi, None, "bvecs"),
                                                         self.buildName(dwi, None, "bvals"))
        else:
            util.symlink(bVecs, self.workingDir)
            util.symlink(bVals, self.workingDir)

        return (self.getImage(self.workingDir, 'grad', None, 'b'),
                self.getImage(self.workingDir, 'grad', None, 'bvecs'),
                self.getImage(self.workingDir, 'grad', None, 'bvals'))


    def stride4DImage(self, source, bEncs, bVecs, bVals, layout="1,2,3"):
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

        images = {'high resolution':self.getImage(self.dependDir, 'anat'),
                  'diffusion weighted':self.getImage(self.dependDir, 'dwi')}
        if self.isSomeImagesMissing(images):
            result = False

        if not (self.getImage(self.dependDir, 'grad', None, 'b') or
                (self.getImage(self.dependDir, 'grad', None, 'bvals')
                 and self.getImage(self.dependDir, 'grad', None, 'bvecs'))):
            self.error("No gradient encoding file found in {}".format(self.dependDir))
            result = False

        return result


    def isDirty(self):

        images = {'gradient .bvals encoding file': self.getImage(self.workingDir, 'grad', None, 'bvals'),
                  'gradient .bvecs encoding file': self.getImage(self.workingDir, 'grad', None, 'bvecs'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
                  'high resolution': self.getImage(self.workingDir, 'anat'),
                  'diffusion weighted': self.getImage(self.workingDir, 'dwi')}

        return self.isSomeImagesMissing(images)


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        anat = self.getImage(self.workingDir, 'anat')
        dwi = self.getImage(self.workingDir, 'dwi')
        anatPng = self.pngSlicerImage(anat)
        dwiGif = self.nifti4dtoGif(dwi)
        
        images = [(anatPng, 'High resolution anatomical image'),
                       (dwiGif, 'Diffusion image')]
        return images
	



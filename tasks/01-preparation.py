from lib.generictask import GenericTask
from lib import util, mriutil

__author__ = 'desmat'


class Preparation(GenericTask):


    def __init__(self, subject):
       GenericTask.__init__(self, subject, 'backup')


    def implement(self):

        dwi = self.getImage(self.dependDir, 'dwi')
        bEnc = self.getImage(self.dependDir, 'grad', None, 'b')
        bVal = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVec = self.getImage(self.dependDir, 'grad', None, 'bvec')

        b0PA = self.getImage(self.dependDir, 'b0PA')
        b0AP = self.getImage(self.dependDir, 'b0AP')

        self.__produceEncodingFiles(bEnc, bVal, bVec)

        if b0PA:
            self.info("Found B0 posterior to anterior image, linking file {} to {}".format(b0AP, self.workingDir))
            util.symlink(b0PA, self.workingDir)

        if b0AP:
            self.info("Found B0 anterior to posterior image, linking file {} to {}".format(b0AP, self.workingDir))
            util.symlink(b0AP, self.workingDir)

        images = {'high resolution': self.getImage(self.dependDir, 'anat'),
                  'diffusion weighted': dwi,
                  'MR magnitude ': self.getImage(self.dependDir, 'mag'),
                  'MR phase ': self.getImage(self.dependDir, 'phase'),
                  'parcellation': self.getImage(self.dependDir,'aparc_aseg'),
                  'freesurfer anatomical': self.getImage(self.dependDir, 'anat', 'freesurfer'),
                  'left hemisphere ribbon': self.getImage(self.dependDir, 'lh_ribbon'),
                  'right hemisphere ribbon': self.getImage(self.dependDir, 'rh_ribbon'),
                  'brodmann': self.getImage(self.dependDir, 'brodmann')}

        for key, value in images.iteritems():
            if value:
                if not mriutil.isDataStridesOrientationExpected(value) \
                        and self.getBoolean("force_realign_strides"):
                    mriutil.strideImage(value, self.buildName(value, "stride"))

                else:
                    self.info("Found {} image, linking file {} to {}".format(key, value, self.workingDir))
                    util.symlink(value, self.workingDir)




    def __produceEncodingFiles(self, bEnc, bVal, bVec):

        #produire les fichiers gradient encoding pour dipy ainsi que mrtrix
        self.info("Produce .b .bval and .bvec gradient file if not existing")
        if not bEnc:
            mriutil.bValBVec2BEnc(bVal, bVec, self.workingDir)
        else:
            util.symlink(bEnc, self.workingDir)

        if not bVal:
            mriutil.bEnc2BVal(bEnc, self.workingDir)
        else:
            util.symlink(bVal, self.workingDir)

        if not bVec:
            mriutil.bEnc2BVec(bEnc, self.workingDir)
        else:
            util.symlink(bVec, self.workingDir)


    def meetRequirement(self, result=True):

        images = {'high resolution':self.getImage(self.dependDir, 'anat'),
                  'diffusion weighted':self.getImage(self.dependDir, 'dwi')}
        if self.isSomeImagesMissing(images):
            result = False

        if not (self.getImage(self.dependDir, 'grad', None, 'b') or
                (self.getImage(self.dependDir, 'grad', None, 'bval')
                 and self.getImage(self.dependDir, 'grad', None, 'bvec'))):
            self.error("No gradient encoding file found in {}".format(self.dependDir))
            result = False

        return result


    def isDirty(self):

        images = {'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
                  'high resolution': self.getImage(self.workingDir, 'anat'),
                  'diffusion weighted': self.getImage(self.workingDir, 'dwi')}

        return self.isSomeImagesMissing(images)


    def qa(self):
        produire les images nécessaires
        produires les métriques et les tâches nécessaire


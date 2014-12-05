from generic.generictask import GenericTask
from modules import util, mriutil
import os

__author__ = 'desmat'


class Preparation(GenericTask):


    def __init__(self, subject):
       GenericTask.__init__(self, subject, 'backup')


    def implement(self):
        self.info("Produce .b .bval and .bvec gradient file if not existing")
        self.__produceEncodingFiles()

        dwi = self.getImage(self.dependDir, 'dwi')

        b0PA = self.getImage(self.dependDir, 'b0PA')
        b0AP = self.getImage(self.dependDir, 'b0AP')

        if b0PA:
            self.info("Found B0 posterior to anterior image, linking file {} to {}".format(b0AP, self.workingDir))
            util.symlink(b0PA, self.workingDir)

        if b0AP:
            self.info("Found B0 anterior to posterior image, linking file {} to {}".format(b0AP, self.workingDir))
            util.symlink(b0AP, self.workingDir)

        if b0PA and (b0AP is False):
            #Produire la carte AP si elle n'existe pas
            self.info("No anterior posterior image found, I will try to produce one")
            b0AP = self.__extractB0APSubVolumeFromDWI(dwi)

        images = {'high resolution': self.getImage(self.dependDir, 'anat'),
                  'diffusion weighted': dwi,
                  'MR magnitude ': self.getImage(self.dependDir, 'mag'),
                  'MR phase ': self.getImage(self.dependDir, 'phase'),
                  'parcellation': self.getImage(self.dependDir,'aparc_aseg'),
                  'anatomical': self.getImage(self.dependDir, 'anat_freesurfer'),
                  'brodmann': self.getImage(self.dependDir, 'brodmann')}

        for key, value in images.iteritems():
            if value:
                self.info("Found {} image, linking file {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)


    def __produceEncodingFiles(self):

        #produire les fichiers gradient encoding pour dipy ainsi que mrtrix
        bEnc = self.getImage(self.dependDir, 'grad', None, 'b')
        bVal = self.getImage(self.dependDir, 'grad', None, 'bval')
        bVec = self.getImage(self.dependDir, 'grad', None, 'bvec')

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


    def __extractB0APSubVolumeFromDWI(self, source):
        self.info("Launch sub volume extraction from mrtrix")

        #rename the file B0
        target = os.path.join(self.workingDir, os.path.basename(source).replace(self.config.get("prefix",'dwi'),self.config.get("prefix",'b0AP')))
        extractAtAxis = self.get('b0AP_extract_at_axis')
        if extractAtAxis not in ["1", "2", "3"]:
            self.error('extract_at_axis must be value of 1 or 2 or 3, found {}'.format(extractAtAxis))

        #make sure that we do not extract a volumes outside of the dimension
        self.info(mriutil.extractSubVolume(source,
                                target,
                                extractAtAxis,
                                self.get("b0AP_extract_at_coordinate"),
                                self.getNTreadsMrtrix()))

        self.info("End extraction from mrtrix")
        return target


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

        #@TODO Implement AP PA dirtyness
        #@TODO Implement mag phase dirtyness
        images = {'gradient .bval encoding file': self.getImage(self.workingDir, 'grad', None, 'bval'),
                  'gradient .bvec encoding file': self.getImage(self.workingDir, 'grad', None, 'bvec'),
                  'gradient .b encoding file': self.getImage(self.workingDir, 'grad', None, 'b'),
                  'high resolution': self.getImage(self.workingDir, 'anat'),
                  'diffusion weighted': self.getImage(self.workingDir, 'dwi')}

        return self.isSomeImagesMissing(images)

from lib.generictask import GenericTask
from lib import util
import glob
import os

__author__ = 'desmat'


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')
        self.id = self.get('id')
        self.setCleanupBeforeImplement(False)

    def implement(self):


        images = {'aparc_aseg': self.getImage(self.dependDir, 'aparc_aseg'),
                    'freesurfer_anat': self.getImage(self.dependDir, 'freesurfer_anat'),
                    'rh_ribbon': self.getImage(self.dependDir, 'rh_ribbon'),
                    'lh_ribbon': self.getImage(self.dependDir, 'lh_ribbon'),
                    'brodmann': self.getImage(self.dependDir, 'brodmann')}


        unlinkedImages = self.__linkExistingImage(images)

        if len(unlinkedImages) > 0:
            self.__submitReconAllIfNeeded()

        if unlinkedImages.has_key('brodmann'):
            self.__createBrodmannAreaImageFromMricronTemplate()
            del(unlinkedImages['brodmann'])

        self.__convertFeesurferImageIntoNifti(unlinkedImages)

        if self.getBoolean('cleanup'):
            self.__cleanup()


    def __submitReconAllIfNeeded(self):
        for image in ["T1.mgz", "aparc+aseg.mgz", "rh.ribbon.mgz", "lh.ribbon.mgz", "norm.mgz", "talairach.m3z"]:
            if not self.__findImageInDirectory(image):
                self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
                os.environ["SUBJECTS_DIR"] = self.workingDir
                anat = self.getImage(self.dependDir, 'anat')
                self.__reconAll(anat)
                break


    def __linkExistingImage(self, images):
        unlinkedImages = {}
        #look for existing map store into preparation and link it so they are not created
        for key, value in images.iteritems():
            if value:
                self.info("Found {} area image, create link from {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)
            else:
                unlinkedImages[key] = value
        return unlinkedImages


    def __convertFeesurferImageIntoNifti(self, images):
        natives = {'freesurfer_anat': "T1.mgz",
                     'aparc_aseg': "aparc+aseg.mgz",
                     'rh_ribbon': "rh.ribbon.mgz",
                     'lh_ribbon': "lh.ribbon.mgz"}

        for key, value in images.iteritems():
            self.__convertAndRestride(self.__findImageInDirectory(natives[key]),  self.get(key))


    def __createBrodmannAreaImageFromMricronTemplate(self):

        brodmannTemplate = os.path.join(self.toadDir, self.get("templates_brodmann"))
        target = self.get("brodmann")
        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir

        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $FREESURFER_HOME/subjects/fsaverage/mri/T1.mgz" \
              " --o brodmann_fsaverage.mgz --regheader --interp nearest".format(brodmannTemplate)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov {0}/mri/norm.mgz --targ brodmann_fsaverage.mgz --s {0} " \
               " --m3z talairach.m3z --o {1} --interp nearest --inv-morph".format(self.id, target)
        self.launchCommand(cmd)
        return self.__convertAndRestride(target, target)


    def __reconAll(self, source):
        """Performs all, or any part of, the FreeSurfer cortical reconstruction

        Args:
            source: The input source file

        """
        self.info("Starting parcellation with freesurfer")

        cmd = "recon-all -{} -i {} -subjid {} -sd {} -openmp {}"\
            .format(self.get('directive'), source, self.id, self.workingDir, self.getNTreads())
        self.info("Log could be found at {}/{}/scripts/recon-all.log".format(self.workingDir, self.id))
        self.launchCommand(cmd, None, None, 777600)


    def __convertAndRestride(self, source, target):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name

        """
        self.info("convert {} image to {} ".format(source, target))
        cmd = "mrconvert {} {} -stride {} -force".format(source, target, self.get('stride_orientation'))
        self.launchCommand(cmd, 'log', 'log')
        return target


    def __findImageInDirectory(self, image):
        for root, dirs, files in os.walk(self.workingDir):
            if image in files:
                return os.path.join(root, image)
        return False


    def __cleanup(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
            self.info("Removing symbolic link {}".format(os.path.join(self.workingDir, source)))
            os.unlink(os.path.join(self.workingDir, source))

        for source in ["brodmann_fsaverage.mgz","brodmann_fsaverage.mgz.lta","brodmann_fsaverage.mgz.reg"]:
            if os.path.isfile(source):
                os.remove(source)

        for source in [self.getImage(self.workingDir, "brodmann", "lta"), self.getImage(self.workingDir, "brodmann", "reg")]:
            if source:
                os.remove(source)

    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.dependDir, 'anat')}
        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {'parcellation': self.getImage(self.workingDir,'aparc_aseg'),
                    'anatomical': self.getImage(self.workingDir,'freesurfer_anat'),
                    'rh_ribbon':self.getImage(self.workingDir,'rh_ribbon'),
                    'lh_ribbon':self.getImage(self.workingDir,'lh_ribbon'),
                    'brodmann':self.getImage(self.workingDir,'brodmann')
                    }
        return self.isSomeImagesMissing(images)

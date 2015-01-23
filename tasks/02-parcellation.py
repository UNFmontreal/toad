from lib.generictask import GenericTask
from lib import util
import glob
import os

__author__ = 'desmat'


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')
        self.id = self.get('id')


    def implement(self):


        images = {'aparc_aseg':self.getImage(self.dependDir, 'aparc_aseg'),
                    'freesurfer_anat':self.getImage(self.dependDir, 'freesurfer_anat'),
                    'rh_ribbon':self.getImage(self.dependDir, 'rh_ribbon'),
                    'lh_ribbon':self.getImage(self.dependDir, 'lh_ribbon'),
                    'brodmann':self.getImage(self.dependDir, 'brodmann')}

        natives = {'freesurfer_anat': "{}/*/mri/T1.mgz",
                     'aparc_aseg': "{}/*/mri/aparc+aseg.mgz",
                     'rh_ribbon': "{}/*/mri/rh.ribbon.mgz",
                     'lh_ribbon': "{}/*/mri/lh.ribbon.mgz"}


        self.__submitReconAllIfNeeded(natives, images)
        unlinkedImages = self.__linkExistingImage(images)
        self.__convertReconAllImageIntoNifti(natives, unlinkedImages)

        #create the brodmann image if not existing
        if not images['brodmann']:
            self.__createBrodmannAreaFromMricronTemplate()

        if self.getBoolean('cleanup'):
            self.__cleanup()

    def __convertReconAllImageIntoNifti(self, natives, images):
        #convert images of interest into nifti
        for key, value in images.iteritems():
            images = glob.glob(natives[key].format(self.workingDir))
            if len(images) > 0:
                self.__convertAndRestride(images.pop(), os.path.join(self.workingDir, self.get(key)))


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


    def __createBrodmannAreaFromMricronTemplate(self):

        brodmannTemplate = os.path.join(self.toadDir, self.get("templates_brodmann"))
        target = self.get("brodmann")

        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $SUBJECTS_DIR/fsaverage/mri/T1.mgz" \
              " --o brodmann_fsaverage.mgz --regheader --interp nearest".format(brodmannTemplate)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov $SUBJECTS_DIR/freesurfer/mri/norm.mgz --s freesurfer --targ brodmann_fsaverage.mgz" \
               " --m3z talairach.m3z --o {} --interp nearest --inv-morph".format(target)
        self.launchCommand(cmd)
        return self.__convertAndRestride(target, target)


    def __submitReconAllIfNeeded(self, natives, images):
        if not (images['aparc_aseg'] and images['freesurfer_anat'] and images['rh_ribbon'] and images['lh_ribbon']):

            for key, value in natives.iteritems():
                images = glob.glob(value.format(self.workingDir))
                if len(images) == 0:
                    missing = True
                else:
                    missing = False

            if missing:
                #recon-all need to be resubmit
                self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
                os.environ["SUBJECTS_DIR"] = self.workingDir
                anat = self.getImage(self.dependDir, 'anat')
                self.__reconAll(anat)


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


    def __cleanup(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
            self.info("Removing symbolic link {}".format(os.path.join(self.workingDir, source)))
            os.unlink(os.path.join(self.workingDir, source))


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
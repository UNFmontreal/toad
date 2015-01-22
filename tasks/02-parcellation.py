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
                    'anat_freesurfer':self.getImage(self.dependDir, 'anat_freesurfer'),
                    'rh_ribbon':self.getImage(self.dependDir, 'rh_ribbon'),
                    'lh_ribbon':self.getImage(self.dependDir, 'lh_ribbon'),
                    'brodmann':self.getImage(self.dependDir, 'brodmann')}

        for key, value in images.iteritems():
            if value:
                self.info("Found {} area image, create link from {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)


        if not (images['aparc_aseg']
                and images['anat_freesurfer']
                and images['rh_ribbon']
                and images['lh_ribbon']
                and images['brodmann']):

            #Skip recon-all if most files could be found Look if freesurfer treee exist and may be exploited
            missing = False
            dicts = {'anat_freesurfer': "{}/*/mri/T1.mgz",
                    'aparc_aseg': "{}/*/mri/aparc+aseg.mgz",
                    'rh_ribbon': "{}/*/mri/rh.ribbon.mgz",
                    'lh_ribbon': "{}/*/mri/lh.ribbon.mgz"}

            for key, value in dicts.iteritems():
                images = glob.glob(value.format(self.workingDir))
                if len(images) == 0:
                   missing = True


            if missing:
                self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
                os.environ["SUBJECTS_DIR"] = self.workingDir

                anat = self.getImage(self.dependDir, 'anat')
                self.__reconAll(anat)

            #convert images of interest into nifti
            for key, value in dicts.iteritems():
                images = glob.glob(value.format(self.workingDir))
                if len(images) > 0:
                    self.__mgz2nii(images.pop(), os.path.join(self.workingDir, self.get(key)))


            #create the brodmann image
            self.__createBrodmannAreaFromMricronTemplate()


    def __createBrodmannAreaFromMricronTemplate(self):

        brodmannTemplate = os.path.join(self.toadDir, self.get("templates_brodmann"))
        target = self.get("brodmann")


        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $SUBJECTS_DIR/fsaverage/mri/T1.mgz" \
              " --o brodmann_fsaverage.nii --regheader --interp nearest".format(brodmannTemplate)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov $SUBJECTS_DIR/freesurfer/mri/norm.mgz --s freesurfer --targ brodmann_fsaverage.nii" \
               " --m3z talairach.m3z --o {} --interp nearest --inv-morph".format(target)
        self.launchCommand(cmd)
        return target


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


    def __mgz2nii(self, source, target):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name

        """
        self.info("convert {} image to {} ".format(source, target))
        cmd = "mrconvert {} {} -stride {}".format(source, target, self.get('stride_orientation'))
        self.launchCommand(cmd, 'log', 'log')


    def __cleanupReconAll(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
            self.info("Removing symbolic link {}".format(os.path.join(self.workingDir, source)))
            os.unlink(os.path.join(self.workingDir,source))


    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.dependDir, 'anat')}
        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {'parcellation': self.getImage(self.workingDir,'aparc_aseg'),
                    'anatomical': self.getImage(self.workingDir,'anat_freesurfer'),
                    'rh_ribbon':self.getImage(self.workingDir,'rh_ribbon'),
                    'lh_ribbon':self.getImage(self.workingDir,'lh_ribbon'),
                    'brodmann':self.getImage(self.workingDir,'brodmann')
                    }
        return self.isSomeImagesMissing(images)
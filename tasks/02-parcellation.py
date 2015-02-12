from lib.generictask import GenericTask
from lib import util
import os

__author__ = 'desmat'


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')
        self.id = self.get('id')
        self.setCleanupBeforeImplement(False)


    def implement(self):

        anat = self.getImage(self.dependDir, 'anat')
        images = {'aparc_aseg': self.getImage(self.dependDir, 'aparc_aseg'),
                    'freesurfer_anat': self.getImage(self.dependDir, 'anat', 'freesurfer'),
                    'rh_ribbon': self.getImage(self.dependDir, 'rh_ribbon'),
                    'lh_ribbon': self.getImage(self.dependDir, 'lh_ribbon'),
                    'brodmann': self.getImage(self.dependDir, 'brodmann')}

        unlinkedImages = self.__linkExistingImage(images)
        if len(unlinkedImages) > 0:
            self.__submitReconAllIfNeeded(anat)

        if unlinkedImages.has_key('brodmann'):
            self.__createBrodmannImage()
            del(unlinkedImages['brodmann'])
            self.__convertFeesurferImageIntoNifti(unlinkedImages, anat)

        if self.getBoolean('cleanup'):
            self.__cleanup()


    def __submitReconAllIfNeeded(self, anatomical):
        for image in ["T1.mgz", "aparc+aseg.mgz", "rh.ribbon.mgz", "lh.ribbon.mgz", "norm.mgz", "talairach.m3z"]:
            if not self.__findImageInDirectory(image):
                treeName = "freesurfer_{}".format(self.getTimestamp().replace(" ","_"))
                if os.path.isdir(self.id):
                    self.info("renaming existing freesurfer tree {} to {}".format(self.id, treeName))
                    os.rename(self.id, treeName)
                self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
                os.environ["SUBJECTS_DIR"] = self.workingDir
                self.__reconAll(anatomical)
                break


    def __linkExistingImage(self, images):
        """
            Create symbolic link for each existing input images into the current working directory.

        Args:
            images: A list of image

        Returns:
            A list of invalid images

        """
        unlinkedImages = {}
        #look for existing map store into preparation and link it so they are not created
        for key, value in images.iteritems():
            if value:
                self.info("Found {} area image, create link from {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)
            else:
                unlinkedImages[key] = value
        return unlinkedImages


    def __convertFeesurferImageIntoNifti(self, images, anatomicalName):

        """
            Convert a List of mgz fresurfer into nifti compress format

        Args:
            images: A list of mgz image
            anatomicalName: The subject anatomical image is need to identify the proper T1

        Returns:
            A list of invalid images

        """
        #@TODO see if we could substitute anatomivalName
        natives = {  'freesurfer_anat': [self.buildName(anatomicalName, 'freesurfer'), "T1.mgz"],
                     'aparc_aseg': [self.get('aparc_aseg'), "aparc+aseg.mgz"],
                     'rh_ribbon': [self.get('rh_ribbon'), "rh.ribbon.mgz"],
                     'lh_ribbon': [self.get('lh_ribbon'), "lh.ribbon.mgz"]}

        for key, value in images.iteritems():
            self.__convertAndRestride(self.__findImageInDirectory(natives[key][1]), natives[key][0])


    def __createBrodmannImage(self):
        """
            Create a brodmann area map

        Returns:
            A brodmann area images

        """
        brodmannTemplate = os.path.join(self.toadDir, self.get("templates_brodmann"))
        target = self.get("brodmann")
        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir

        #@TODO remove all trace of mgz file
        cmd = "mri_vol2vol --mov {} --targ $FREESURFER_HOME/subjects/fsaverage/mri/T1.mgz" \
              " --o brodmann_fsaverage.mgz --regheader --interp nearest".format(brodmannTemplate)
        self.launchCommand(cmd)

        cmd =  "mri_vol2vol --mov $SUBJECTS_DIR/{0}/mri/norm.mgz --targ brodmann_fsaverage.mgz --s {0} " \
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
        """Utility method that look if a input image could be found in a directory and his subdirectory

        Args:
            image: an input image name

        Returns:
            the file name if found, False otherwise

        """
        for root, dirs, files in os.walk(os.path.join(self.workingDir, self.id)):
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

        images = {'parcellation': self.getImage(self.workingDir, 'aparc_aseg'),
                    'anatomical': self.getImage(self.workingDir, 'anat', 'freesurfer'),
                    'rh_ribbon':self.getImage(self.workingDir, 'rh_ribbon'),
                    'lh_ribbon':self.getImage(self.workingDir, 'lh_ribbon'),
                    'brodmann':self.getImage(self.workingDir, 'brodmann')}
        return self.isSomeImagesMissing(images)


    def qaSupplier(self):

        anatFreesurfer = self.getImage(self.workingDir, 'anat', 'freesurfer')
        aparcAseg = self.getImage(self.workingDir, 'aparc_aseg')
        brodmann = self.getImage(self.workingDir, 'brodmann')
        self.pngSlicerImage(anatFreesurfer)
        self.c3dSegmentation(anatFreesurfer, aparcAseg, '2', '0.5')
        self.c3dSegmentation(anatFreesurfer, brodmann, '2', '0.5')
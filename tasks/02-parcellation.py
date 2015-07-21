import os
import numpy
import scipy
import nibabel
from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil

__author__ = 'desmat'


class Parcellation(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation', 'qa')
        self.id = self.get('id')
        self.setCleanupBeforeImplement(False)


    def implement(self):
 
        anat = self.getImage(self.dependDir, 'anat')

        #look if a freesurfer tree is already available
        if not  self.__findAndLinkFreesurferStructure():
            self.__submitReconAll(anat)

        self.__convertFeesurferImageIntoNifti(anat)
        self.__createBrodmannImage()
        self.__createSegmentationMask(self.get('aparc_aseg'), self.get('mask'))

        if self.getBoolean('cleanup'):
            self.__cleanup()

        #QA
        workingDirAnat = self.getImage(self.workingDir, 'anat', 'freesurfer')
        aparcAseg = self.getImage(self.workingDir, 'aparc_aseg')
        brodmann = self.getImage(self.workingDir, 'brodmann')
        norm = self.getImage(self.workingDir, 'norm')
        mask = self.getImage(self.workingDir, 'mask')

        anatPng = self.buildName(workingDirAnat, None, 'png')
        aparcAsegPng = self.buildName(aparcAseg, None, 'png')
        brodmannPng = self.buildName(brodmann, None, 'png')
        normPng = self.buildName(norm, None, 'png')
        maskPng = self.buildName(mask, None, 'png')

        self.slicerPng(workingDirAnat, anatPng, boundaries=aparcAseg)
        self.slicerPng(workingDirAnat, normPng, boundaries=norm)
        self.slicerPng(workingDirAnat, aparcAsegPng, segOverlay=aparcAseg, boundaries=aparcAseg)
        self.slicerPng(workingDirAnat, brodmannPng, segOverlay=brodmann, boundaries=brodmann)
        self.slicerPng(workingDirAnat, maskPng, segOverlay=mask, boundaries=mask)


    def __findAndLinkFreesurferStructure(self):
        """Look if a freesurfer structure already exists in the backup.

        freesurfer structure will be link and id will be update

        Returns:
            Return the linked directory name if a freesurfer structure is found, False otherwise
        """
        freesurferStructure = os.path.join(self.dependDir, self.id)
        if mriutil.isAfreesurferStructure(freesurferStructure):
           self.info("{} seem\'s a valid freesurfer structure: moving it to {} directory".format(freesurferStructure, self.workingDir))
           util.symlink(freesurferStructure, self.id)
           return True
        return False


    def __submitReconAll(self, anatomical):
        """Submit recon-all on the anatomical image
        Args:
            anatomical: the high resolution image
        """
        treeName = "freesurfer_{}".format(self.getTimestamp().replace(" ","_"))

        #backup already existing tree
        if os.path.isdir(self.id):
            self.info("renaming existing freesurfer tree {} to {}".format(self.id, treeName))
            os.rename(self.id, treeName)

        self.info("Starting parcellation with freesurfer")
        self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
        os.environ["SUBJECTS_DIR"] = self.workingDir
        cmd = "recon-all -{} -i {} -subjid {} -sd {} -openmp {}"\
            .format(self.get('directive'), anatomical, self.id, self.workingDir, self.getNTreads())
        self.info("Log could be found at {}/{}/scripts/recon-all.log".format(self.workingDir, self.id))
        self.launchCommand(cmd, None, None, 86400)


    def __convertFeesurferImageIntoNifti(self, anatomicalName):

        """
            Convert a List of mgz fresurfer into nifti compress format

        Args:
            anatomicalName: The subject anatomical image is need to identify the proper T1

        """
        for (target, source) in [(self.buildName(anatomicalName, 'freesurfer'), "T1.mgz"),
                                    (self.get('aparc_aseg'), "aparc+aseg.mgz"),
                                    (self.get('rh_ribbon'), "rh.ribbon.mgz"),
                                    (self.get('lh_ribbon'), "lh.ribbon.mgz"),
                                    (self.get('norm'), "norm.mgz")]:

            self.__convertAndRestride(self.__findImageInDirectory(source, os.path.join(self.workingDir, self.id)), target)


    def __createBrodmannImage(self):
        """
            Create a brodmann area map

        Returns:
            A brodmann area images

        """
        brodmannTemplate = os.path.join(self.toadDir, "templates", "mri", self.get("templates_brodmann"))
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


    def __convertAndRestride(self, source, target):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name

        """
        self.info("convert {} image to {} ".format(source, target))
        cmd = "mrconvert {} {} -stride {} -force -quiet"\
            .format(source, target, self.config.get('preparation', 'stride_orientation'))
        self.launchCommand(cmd)
        return target


    def __findImageInDirectory(self, image, freesurferDirectory):
        """Utility method that look if a input image could be found in a directory and his subdirectory

        Args:
            image: an input image name
            freesurferDirectory: the location of the freesurfer structure
        Returns:
            the file name if found, False otherwise

        """
        for root, dirs, files in os.walk(freesurferDirectory):
            if image in files:
                return os.path.join(root, image)
        return False


    def __createSegmentationMask(self, source, target):
        """
        Compute mask from freesurfer segmentation : aseg then morphological operations

        Args:
            source: The input source file
            target: The name of the resulting output file name
        """

        nii = nibabel.load(source)
        op = ((numpy.mgrid[:5,:5,:5]-2.0)**2).sum(0)<=4
        mask = scipy.ndimage.binary_closing(nii.get_data()>0, op, iterations=2)
        scipy.ndimage.binary_fill_holes(mask, output=mask)
        nibabel.save(nibabel.Nifti1Image(mask.astype(numpy.uint8), nii.get_affine()), target)
        del nii, mask, op
        return target


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


    def __cleanup(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        #for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
        #    linkName = os.path.join(self.workingDir, source)
        #    self.info("Removing symbolic link {}".format(linkName))
        #    if os.path.islink(linkName):
        #        os.unlink(linkName)
        
	for source in ["brodmann_fsaverage.mgz", "brodmann_fsaverage.mgz.lta", "brodmann_fsaverage.mgz.reg"]:
            if os.path.isfile(source):
                os.remove(source)

        for source in [self.getImage(self.workingDir, "brodmann", None, "lta"), self.getImage(self.workingDir, "brodmann", None, "reg")]:
            if source:
                os.remove(source)

    def meetRequirement(self):

        images = Images((self.getImage(self.dependDir, 'anat'), 'high resolution'))
        return images.isAllImagesExists()


    def isDirty(self):

        images = Images((self.getImage(self.workingDir, 'aparc_aseg'), 'parcellation'),
                  (self.getImage(self.workingDir, 'anat', 'freesurfer'), 'anatomical'),
                  (self.getImage(self.workingDir, 'rh_ribbon'), 'rh_ribbon'),
                  (self.getImage(self.workingDir, 'lh_ribbon'), 'lh_ribbon'),
                  (self.getImage(self.workingDir, 'brodmann'), 'brodmann'),
                  (self.getImage(self.workingDir, 'norm'), 'norm'),
                  (self.getImage(self.workingDir, 'mask'), 'freesurfer masks'))

        return images.isSomeImagesMissing()


    def qaSupplier(self):
        
        anatFreesurferPng = self.getImage(self.workingDir, 'anat', 'freesurfer', ext='png')
        aparcAsegPng = self.getImage(self.workingDir, 'aparc_aseg', ext='png')
        brodmannPng = self.getImage(self.workingDir, 'brodmann', ext='png')
        maskPng = self.buildName(self.getImage(self.workingDir, 'mask'), None, 'png')
        normPng = self.buildName(self.getImage(self.workingDir, 'norm'), None, 'png')

        return Images((anatFreesurferPng, 'High resolution anatomical image of freesurfer'),
                       (aparcAsegPng, 'Aparc aseg segmentation from freesurfer'),
                       (maskPng, 'mask from freesurfer'),
                       (brodmannPng, 'Brodmann segmentation from freesurfer'),
                       (normPng, 'Normalize image from freesurfer'))


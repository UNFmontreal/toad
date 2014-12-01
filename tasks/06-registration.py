from generic.generictask import GenericTask
import os

__author__ = 'desmat'

class Registration(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preprocessing', 'parcellation', 'preparation')


    def implement(self):

        anatWMFile = self.getImage(self.dependDir,'anat','wm')
        anatBrainFile = self.getImage(self.dependDir,'anat','brain')
        b0WMFile = self.getImage(self.dependDir,'b0','wm')
        anatFreesurfer = self.getImage(self.parcellationDir,'anat_freesurfer')
        aparcAsegFile =  self.getImage(self.parcellationDir,'aparc_aseg')
        brodmannFile =  self.getImage(self.parcellationDir,'brodmann')


        anatBrainTransformation = self.__registration(anatBrainFile, b0WMFile)
        anatBrainResampled = self.__resample(anatBrainFile, b0WMFile, anatBrainTransformation, False)

        anatWMTransformation = self.__registration(anatWMFile, b0WMFile)
        anatWMResampled = self.__resample(anatWMFile, b0WMFile, anatWMTransformation, False)
        anatFreesurferResampled = self.__resample(anatFreesurfer, b0WMFile, anatWMTransformation, False)
        aparcAsegFilesResampled = self.__resample(aparcAsegFile, b0WMFile, anatWMTransformation, True)
        brodmannFileResampled = self.__resample(brodmannFile, b0WMFile, anatWMTransformation, True)


    def __registration(self, movingImage, fixedImage):
        """Register an image with symmetric normalization and mutual information metric

        Args:
            movingImage:
            fixedImage:

        Returns:
            return a file containing the resulting transformation
        """
        self.info("Starting registration from ants")
        name = os.path.basename(movingImage).replace(".nii","")
        target = self.getTarget(name, "transformation", ".txt")

        cmd = "ANTS {} --MI-option {} --image-metric {}[{} ,{} ,{} ,{} ] --number-of-affine-iterations {}" \
              " --output-naming {} --transformation-model {} --use-Histogram-Matching {}"\
              .format(self.get('dimension'),
                self.get('mi_option'),
                self.get('metric'),
                fixedImage,
                movingImage,
                self.get('metric_weight'),
                self.get('radius'),
                self.get('number_of_affine_iterations'),
                name,
                self.config.get('registration','transformation_model'),
                self.config.get('registration','use_histogram_matching'))

        self.getNTreadsAnts()
        self.launchCommand(cmd)

        self.info('Renaming {}Affine.txt to {}'.format(name, target))
        os.rename('{}Affine.txt'.format(name), target)

        if (self.getBoolean("cleanup")):
            self.info("Removing extra file {}InverseWarp.nii.gz".format(name))
            os.remove('{}InverseWarp.nii.gz'.format(name))
            self.info("Removing extra file {}Warp.nii.gz".format(name))
            os.remove('{}Warp.nii.gz'.format(name))

        self.info("End registration from ants")
        return target


    def __resample (self, source, referenceImage, transformation, use_NN):
        """Resample (align) a source image to the refImage

        Args:
            source: the image that you want to resample
            referenceImage: the image of reference
            transformation: the transformation file resulting from the registration
            use_NN: if we should use nearest neighbourhood algorithm

        Return:
            the resulting resampled image name

        """
        self.info("Apply transformation with ants")
        target = self.getTarget(source, "resample")

        cmd = "WarpImageMultiTransform {} {} {} -R {} {} "\
            .format(self.get('dimension'), source, target, referenceImage, transformation)
        if use_NN:
            cmd += "--use-NN "

        self.getNTreadsAnts()
        self.launchCommand(cmd)

        self.info("End applying transformation with ants")
        return target


    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.preparationDir, 'anat'),
                  'white matter segmented high resolution': self.getImage(self.dependDir,'anat','wm'),
                  'brain extracted high resolution': self.getImage(self.dependDir,'anat','brain'),
                  'white matter segmented high resolution':self.getImage(self.dependDir,'b0','wm'),
                  'white matter segmented B0': self.getImage(self.dependDir,'anat','wm'),
                  'parcellation': self.getImage(self.parcellationDir, 'aparc_aseg'),
                  'high resolution freesurfer': self.getImage(self.parcellationDir, 'anat_freesurfer'),
                  'brodmann': self.getImage(self.parcellationDir, 'brodmann')}

        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {'freesurfer anatomical': self.getImage(self.workingDir,'anat_freesurfer', 'resample'),
                  'parcellation': self.getImage(self.workingDir,'aparc_aseg', 'resample'),
                  'brodmann': self.getImage(self.workingDir,'brodmann', 'resample'),
                  'white matter segmented high resolution resampled': self.getImage(self.workingDir,'anat', ['brain','wm','resample']),
                  'high resolution resampled imgage':self.getImage(self.workingDir,'anat', ['brain','resample'])}

        return self.isSomeImagesMissing(images)

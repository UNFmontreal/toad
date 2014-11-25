from generic.generictask import GenericTask
from modules import util
import glob
import os

__author__ = 'desmat'


class Parcellation(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')
        self.id = subject.getConfig().get('parcellation', 'id')


    def implement(self):

        images = {'parcellation':self.getImage(self.dependDir,'aparc_aseg'),
                  'anatomical':self.getImage(self.dependDir,'anat_freesurfer'),
                  'brodmann':self.getImage(self.dependDir,'brodmann')}

        for key, value in images.iteritems():
            if value:
                self.info("Found %s area image, create link from %s to %s"%(key, value, self.workingDir))
                util.symlink(value, self.workingDir)

        if not (images['parcellation'] and images['anatomical'] and images['brodmann']):

            self.info("Set SUBJECTS_DIR to %s"%self.workingDir)
            os.environ["SUBJECTS_DIR"] = self.workingDir

            anat = self.getImage(self.dependDir, 'anat')
            self.__reconAll(anat)
            self.__createBrodmannArea()

            #@TODO refactor this block of code
            if not images['anatomical']:
                anatMgzFreesurfers = glob.glob("%s/%s/mri/T1.mgz"%(self.workingDir, self.id))
                for anatMgzFreesurfer in anatMgzFreesurfers:
                    outputFile = os.path.join(self.workingDir,self.get('anat_freesurfer'))
                    self.__mgz2nii(anatMgzFreesurfer, outputFile)

            if not images['parcellation']:
                aparcMgzAsegs = glob.glob("%s/%s/mri/aparc+aseg.mgz"%(self.workingDir, self.id))
                for aparcMgzAseg in aparcMgzAsegs:
                    outputFile = os.path.join(self.workingDir, self.get('aparc_aseg'))
                    self.__mgz2nii(aparcMgzAseg, outputFile)

            if not images['brodmann']:
                brodmanns = glob.glob("%s/%s/mri/brodmann.mgz"%(self.workingDir, self.id))
                for brodmann in brodmanns:
                    outputFile = os.path.join(self.workingDir, self.get('brodmann'))
                    self.__mgz2nii(brodmann, outputFile)


    def __reconAll(self, source):
        """Performs all, or any part of, the FreeSurfer cortical reconstruction

        Args:
            source: The input source file

        """
        self.info("Starting parcellation with freesurfer")

        cmd = "recon-all -%s -i %s -subjid %s -sd %s -openmp %s"\
             %(self.get('directive'), source, self.id, self.workingDir, self.getNTreads())
        self.info("Logging into %s/%s/scripts/recon-all.log"%(self.workingDir, self.id))
        self.launchCommand(cmd, None, None)


    def __createBrodmannArea(self):
        """create a Brodmann Area image

        """
        toadLabelsDir = os.path.join(self.toadDir, self.config.get("parcellation", "labels_dir"))
        labels = glob.glob("%s/*.label"%toadLabelsDir)

        rhAnnotLabels =""
        lhAnnotLabels =""
        for labelDir in labels:
            label = os.path.basename(labelDir)
            hemisphere = label.split(".")[0]
            if hemisphere == "rh":
                rhAnnotLabels += "--l %s/%s/label/%s "%(self.workingDir, self.id,label)
            if hemisphere == "lh":
                lhAnnotLabels += "--l %s/%s/label/%s "%(self.workingDir, self.id,label)

            cmd = "mri_label2label --srcsubject fsaverage --srclabel %s --trgsubject %s --trglabel %s --hemi %s --regmethod surface"%(labelDir, self.id, label, hemisphere)
            self.launchCommand(cmd, 'log')

        annotation = self.get('annotation')
        cmd = "mris_label2annot --s %s --h rh --ctab $FREESURFER_HOME/FreeSurferColorLUT.txt --a %s %s"%(self.id, annotation, rhAnnotLabels)
        self.launchCommand(cmd, 'log')

        cmd = "mris_label2annot --s %s --h lh --ctab $FREESURFER_HOME/FreeSurferColorLUT.txt --a %s %s"%(self.id, annotation, lhAnnotLabels)
        self.launchCommand(cmd, 'log')

        cmd = "mri_aparc2aseg --s %s --annot %s --o %s/%s/mri/%s"%(self.id, annotation, self.workingDir, self.id, self.get('brodmann_mgz'))
        self.launchCommand(cmd, 'log')


    def __mgz2nii(self, source, target, inType='mgz', outType='nii'):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name
            inType: The image format of the original file. Default: mgz
            outType: The format of the resulting output image. Default: nii

        """
        self.info("convert %s image to %s "%(source, target))
        cmd = "mri_convert -it %s -ot %s %s %s"%(inType, outType, source, target)
        util.launchCommand(cmd)


    def __cleanupReconAll(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
            self.info("Removing symbolic link %s"%os.path.join(self.workingDir, source))
            os.unlink(os.path.join(self.workingDir,source))


    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.dependDir, 'anat')}
        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {'parcellation': self.getImage(self.workingDir,'aparc_aseg'),
                  'anatomical': self.getImage(self.workingDir,'anat_freesurfer'),
                  'brodmann': self.getImage(self.workingDir,'brodmann')}

        return self.isSomeImagesMissing(images)



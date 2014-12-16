from lib.generictask import GenericTask
import os


__author__ = 'desmat'

class HardiMetric(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'hardi', 'masking')


    def implement(self):
        fodImage = self.getImage(self.dependDir, 'dwi', 'fod')
        mask = self.getImage(self.maskingDir, 'anat',['extended','mask'])
        self.__fod2metric(fodImage, mask)


    def __fod2metric(self, source, mask=None):
        self.info("Starting fod2metric creation from mrtrix on {}".format(source))

        images = {'gfaImage': self.buildName(source, 'gfa'),
        'gfaTmp':self.buildName(self.workingDir, "tmp", 'nii'),
        'nufoImage':self.buildName(source, 'nufo'),
        'nufoTmp':self.buildName(self.workingDir,"tmp1", 'nii'),
        'fixelPeakImage':self.buildName(self.workingDir,"tmp1", 'nii'),
        'fixelPeakTmp':self.buildName(self.workingDir,"tmp",'msf','nii')}

        cmd = "fod2metric {} -gfa {} -count {} -fixel_peak {} -nthreads {} -force -quiet"\
            .format(source, images['gfaTmp'], images['nufoTmp'], images['fixelPeakTmp'], self.getNTreadsMrtrix())
        if mask is not None:
            cmd += " -mask {} ".format(mask)

        self.launchCommand(cmd)
        for prefix in ["gfa", "nufo", "fixelPeak" ]:
            self.info("renaming {} to {}".format(images["{}Tmp".format(prefix)], images["{}Image".format(prefix)]))
            os.rename(images["{}Tmp".format(prefix)], images["{}Image".format(prefix)])


    def meetRequirement(self):

        images = {'constrained spherical deconvolution': self.getImage(self.dependDir, 'dwi', 'fod'),
                    'ultimate extended mask': self.getImage(self.maskingDir, 'anat',['extended','mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {"Generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi','gfa'),
                  'nufo': self.getImage(self.workingDir,'dwi','nufo')}
        return self.isSomeImagesMissing(images)

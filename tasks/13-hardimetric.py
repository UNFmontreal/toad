from generic.generictask import GenericTask
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
        self.info("Starting fod2metric creation from mrtrix on %s"%source)

        images = {'gfaImage': self.getTarget(source, 'gfa'),
        'gfaTmp':self.getTarget(self.workingDir, "tmp", 'nii'),
        'nufoImage':self.getTarget(source, 'nufo'),
        'nufoTmp':self.getTarget(self.workingDir,"tmp1", 'nii'),
        'fixelPeakImage':self.getTarget(self.workingDir,"tmp1", 'nii'),
        'fixelPeakTmp':self.getTarget(self.workingDir,"tmp",'msf','nii')}

        cmd = "fod2metric %s -gfa %s -count %s -fixel_peak %s -nthreads %s -force"%(source, images['gfaTmp'], images['nufoTmp'], images['fixelPeakTmp'], self.getNTreadsMrtrix())
        if mask is not None:
            cmd += " -mask %s "%mask

        self.launchCommand(cmd)
        for prefix in ["gfa", "nufo", "fixelPeak" ]:
            self.info("renaming %s to %s"%(images["%sTmp"%(prefix)], images["%sImage"%(prefix)]))
            os.rename(images["%sTmp"%(prefix)], images["%sImage"%(prefix)])

        #@TODO remove comment
        #self.info("renaming %s to %s"%(gfaTmp, gfaImage))
        #os.rename(gfaTmp, gfaImage)
        #self.info("renaming %s to %s"%(nufoTmp, nufoImage))
        #os.rename(nufoTmp, nufoImage)
        #self.info("renaming %s to %s"%(fixelPeakTmp, fixelPeakImage))
        #os.rename(fixelPeakTmp, fixelPeakImage)


    def meetRequirement(self):

        images = {'constrained spherical deconvolution': self.getImage(self.dependDir, 'dwi', 'fod'),
                    'ultimate extended mask': self.getImage(self.maskingDir, 'anat',['extended','mask'])}
        return self.isAllImagesExists(images)


    def isDirty(self, result = False):

        images = {"Generalised Fractional Anisotropy": self.getImage(self.workingDir,'dwi','gfa'),
                  'nufo': self.getImage(self.workingDir,'dwi','nufo')}
        return self.isSomeImagesMissing(images)

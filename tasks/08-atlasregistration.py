from core.toad.generictask import GenericTask
from lib.images import Images
from lib import mriutil

__author__ = "Your_name"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Your_name", "Mathieu Desrosiers"]


class Atlasregistration(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'atlas', 'upsampling', 'registration')

    def implement(self):

        b0 = self.getUpsamplingImage('b0','upsample')
        mrtrixMatrix =  self.getRegistrationImage("freesurfer_dwi", ["transformation", "mrtrix"], "mat")
        freesurferToDWI = self.getRegistrationImage("freesurfer_dwi", "transformation", "mat")

        brodmann = self.getAtlasImage("brodmann")
        aal2 = self.getAtlasImage("aal2")
        networks7 = self.getAtlasImage("networks7")

        brodmannRegister = mriutil.applyRegistrationMrtrix(brodmann, mrtrixMatrix, self.buildName(brodmann, "register"))
        mriutil.applyResampleFsl(brodmann, b0, freesurferToDWI, self.buildName(brodmann, "resample"), True)

        aal2Register = mriutil.applyRegistrationMrtrix(aal2, mrtrixMatrix, self.buildName(aal2, "register"))
        mriutil.applyResampleFsl(aal2, b0, freesurferToDWI, self.buildName(aal2, "resample"), True)

        networks7Register = mriutil.applyRegistrationMrtrix(networks7, mrtrixMatrix, self.buildName(networks7, "register"))
        mriutil.applyResampleFsl(networks7, b0, freesurferToDWI, self.buildName(networks7, "resample"), True)


    def meetRequirement(self):
        return Images(self.getUpsamplingImage('b0','upsample'),
                      self.getRegistrationImage("freesurfer_dwi", ["transformation", "mrtrix"], "mat"),
                      self.getRegistrationImage("freesurfer_dwi", "transformation", "mat"),
                      self.getAtlasImage("brodmann"),
                      self.getAtlasImage("aal2"),
                      self.getAtlasImage("networks7"))


    def isDirty(self):
        return Images((self.getImage('brodmann', 'resample'), 'brodmann atlas  resample'),
                  (self.getImage('aal2', 'resample'), 'aal2 atlas resample'),
                  (self.getImage('networks7', 'resample'), 'Resting state sevens networks atlas resample'))


    def qaSupplier(self):
        b0 = self.getUpsamplingImage('b0','upsample')
        brainMask = self.getRegistrationImage('mask', 'resample')
        brodmann = self.getImage('brodmann', 'resample')
        aal2 = self.getImage('aal2', 'resample')
        networks7 = self.getImage('networks7', 'resample')
        brodmannPng = self.buildName(brodmann, None, 'png')
        aal2Png = self.buildName(aal2, None, 'png')
        networks7Png = self.buildName(networks7, None, 'png')
        self.slicerPng(b0, brodmannPng, segOverlay=brodmann, boundaries=brainMask)
        self.slicerPng(b0, aal2Png, segOverlay=aal2, boundaries=brainMask)
        self.slicerPng(b0, networks7Png, segOverlay=networks7, boundaries=brainMask)

        qaImages = Images((brodmannPng, 'Brodmann segmentation on upsampled b0'),
        (aal2Png, 'Aal2 segmentation on upsampled b0'),
        (networks7Png, 'Resting state sevens networks segmentation on upsampled b0'))

        return qaImages
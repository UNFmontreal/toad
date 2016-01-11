# -*- coding: utf-8 -*-
import os
import random
import shutil

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Masking(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'registration', 'upsampling', 'qa')


    def implement(self):
        aparcAsegRegister = self.getRegistrationImage("aparc_aseg", "register")
        aparcAsegResample = self.getRegistrationImage("aparc_aseg", "resample")
        maskRegister = self.getRegistrationImage("mask", "register")
        maskResample = self.getRegistrationImage("mask", "resample")

        tt5Register = self.getRegistrationImage("tt5", "register")
        tt5Resample = self.getRegistrationImage("tt5", "resample")
        #Produces a mask image suitable for seeding streamlines from the grey matter - white matter interface
        seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)

        #create a area 253 mask and a 1014 mask
        self.info(mriutil.mrcalc(aparcAsegResample, '253', self.buildName('aparc_aseg', ['253', 'mask'], 'nii.gz')))
        self.info(mriutil.mrcalc(aparcAsegResample, '1024', self.buildName('aparc_aseg', ['1024', 'mask'],'nii.gz')))

        #produce optionnal mask
        if self.get("start_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'start')
        if self.get("stop_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'stop')
        if self.get("exclude_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'exclude')

        #extract the white matter mask from the act
        whiteMatterAct = self.__extractWhiteMatterFrom5tt(tt5Resample)

        colorLut =  os.path.join(self.toadDir, "templates", "lookup_tables", self.get("template", "freesurfer_lut"))
        self.info("Copying {} file into {}".format(colorLut, self.workingDir))
        shutil.copy(colorLut, self.workingDir)


    def __createRegionMaskFromAparcAseg(self, source, operand):

        option = "{}_seeds".format(operand)
        self.info("Extract {} regions from {} image".format(operand, source))
        regions = util.arrayOfInteger(self.get( option))
        self.info("Regions to extract: {}".format(regions))

        target = self.buildName(source, [operand, "extract"])
        structures = mriutil.extractStructure(regions, source, target)
        self.__createMask(structures)


    def __extractWhiteMatterFrom5tt(self, source):
        """Extract the white matter part from the act

        Args:
            An 5tt image

        Returns:
            the resulting file filename

        """

        target = self.buildName(source, ["wm", "mask"])
        self.info(mriutil.extractSubVolume(source,
                                target,
                                self.get('act_extract_at_axis'),
                                self.get("act_extract_at_coordinate"),
                                self.getNTreadsMrtrix()))
        return target


    def __launch5tt2gmwmi(self, source):
        """Generate a mask image appropriate for seeding streamlines on the grey
           matter - white matter interface

        Args:
            source: the input 5TT segmented anatomical image

        Returns:
            the output mask image
        """

        tmp = 'tmp_5tt2gmwmi_{0:.6g}.nii.gz'.format(random.randint(0,999999))
        target = self.buildName(source, "5tt2gmwmi")
        self.info("Starting 5tt2gmwmi creation from mrtrix on {}".format(source))

        cmd = "5tt2gmwmi {} {} -nthreads {} -quiet".format(source, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        return self.rename(tmp, target)


    def __createMask(self, source):
        self.info("Create mask from {} images".format(source))
        self.info(mriutil.fslmaths(source, self.buildName(source, 'mask'), 'bin'))


    def meetRequirement(self):
        return Images((self.getRegistrationImage("aparc_aseg", "resample"), 'resampled parcellation atlas'),
                    (self.getRegistrationImage("aparc_aseg", "register"), 'register parcellation atlas'),
                    (self.getRegistrationImage('mask', 'resample'),  'brain extracted, resampled high resolution'),
                    (self.getRegistrationImage('mask', 'register'),  'brain extracted, register high resolution'),
                    (self.getRegistrationImage('tt5', 'resample'),  '5tt resample'),
                    (self.getRegistrationImage('tt5', 'register'),  '5tt register'))

    def isDirty(self):
        images = Images((self.getImage('aparc_aseg',['253','mask']), 'area 253 from aparc_aseg atlas'),
                     (self.getImage('aparc_aseg',['1024','mask']), 'area 1024 from aparc_aseg atlas'),
                     (self.getImage("tt5", ["resample", "wm", "mask"]), 'resample white segmented mask'),
                     (self.getImage("tt5", ["register", "5tt2gmwmi"]), 'grey matter, white matter interface'))

        if self.get("start_seeds").strip() != "":
            images.append((self.getImage('aparc_aseg', ['resample', 'start', 'extract', 'mask']), 'high resolution, start, brain extracted mask'))
            images.append((self.getImage('aparc_aseg', ['resample', 'start', 'extract']), 'high resolution, start, brain extracted'))

        if self.get("stop_seeds").strip() != "":
            images.append((self.getImage('aparc_aseg', ['resample', 'stop', 'extract', 'mask']), 'high resolution, stop, brain extracted mask'))
            images.append((self.getImage('aparc_aseg', ['resample', 'stop', 'extract']), 'high resolution, stop, brain extracted'))

        if self.get("exclude_seeds").strip() != "":
            images.append((self.getImage('aparc_aseg', ['resample', 'exclude', 'extract', 'mask']), 'high resolution, excluded, brain extracted, mask'))
            images.append((self.getImage('aparc_aseg', ['resample', 'exclude', 'extract']), 'high resolution, excluded, brain extracted'))

        return images


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        #Get images
        b0 = self.getUpsamplingImage('b0', 'upsample')
        whiteMatter = self.getImage("tt5", ["resample", "wm", "mask"])
        interfaceGmWm = self.getImage("tt5", ["register", "5tt2gmwmi"])
        area253 = self.getImage('aparc_aseg',['253','mask'])
        area1024 = self.getImage('aparc_aseg',['1024','mask'])

        #Build qa images
        tags = (
            (whiteMatter, 'resample white segmented mask'),
            #(interfaceGmWm, 'grey matter, white matter interface'),
            #(area253, 'area 253 from aparc_aseg atlas'),
            #(area1024, 'area 1024 from aparc_aseg atlas'),
            )
        for image, description in tags:
            imageQa = self.plot3dVolume(b0, edges=image, fov=image)
            qaImages.append((imageQa, description))

        return qaImages

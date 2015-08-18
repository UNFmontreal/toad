import random
import shutil
import os
from core.generictask import GenericTask
from lib.images import Images
from lib import util, mriutil


__author__ = 'desmat'


class Masking(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'registration', 'preparation', 'eddy' 'qa')


    def implement(self):
        aparcAsegRegister = self.getImage(self.dependDir,"aparc_aseg", "register")
        aparcAsegResample = self.getImage(self.dependDir,"aparc_aseg", "resample")
        maskRegister = self.getImage(self.dependDir,"mask", "register")
        maskResample = self.getImage(self.dependDir,"mask", "resample")

        tt5Register = self.getImage(self.dependDir,"tt5", "register")
        tt5Resample = self.getImage(self.dependDir,"tt5", "resample")
        #Produces a mask image suitable for seeding streamlines from the grey matter - white matter interface
        seed_gmwmi = self.__launch5tt2gmwmi(tt5Register)

        #extended = self.buildName('anat', ['resample', 'extended'])
        #self.info("Add {} and {} images together in order to create the ultimate image"
        #          .format(anatBrainResample, aparcAsegResample))

        #self.info(mriutil.fslmaths(anatBrainResample, extended, 'add', aparcAsegResample))
        #self.__createMask(extended)
        #self.__createMask(aparcAsegResample)

        #create a area 253 mask and a 1014 mask
        self.info(mriutil.mrcalc(aparcAsegResample, '253', self.buildName('aparc_aseg', ['253','mask'], 'nii.gz')))
        self.info(mriutil.mrcalc(aparcAsegResample, '1024', self.buildName('aparc_aseg', ['1024','mask'],'nii.gz')))

        #produce optionnal mask
        if self.get("start_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'start')
        if self.get("stop_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'stop')
        if self.get("exclude_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'exclude')

        #Launch act_anat_prepare_freesurfer
        #@TODO register and resampling act
        #actRegister = self.__actAnatPrepareFreesurfer(aparcAsegRegister)
        #actResample = self.__actAnatPrepareFreesurfer(aparcAsegResample)

        #extract the white matter mask from the act
        whiteMatterAct = self.__extractWhiteMatterFrom5tt(tt5Resample)

        colorLut =  os.path.join(self.toadDir, "templates", "lookup_tables", self.get("template", "freesurfer_lut"))
        self.info("Copying {} file into {}".format(colorLut, self.workingDir))
        shutil.copy(colorLut, self.workingDir)

        #QA
        dwi = self.getImage(self.eddyDir, 'dwi')
        bVals=  self.getImage(self.preparationDir, 'grad',  None, 'bvals')
        b0 = os.path.join(self.workingDir, os.path.basename(dwi).replace(self.get("prefix", 'dwi'), self.get("prefix", 'b0')))
        self.info(mriutil.extractFirstB0FromDwi(dwi, b0, bVals)) 

        seed_gmwmiPng = self.buildName(seed_gmwmi, None, 'png')
        whiteMatterActPng = self.buildName(whiteMatterAct, None, 'png')

        self.slicerPng(b0, seed_gmwmiPng, maskOverlay=seed_gmwmi, boundaries=seed_gmwmi)
        self.slicerPng(b0, whiteMatterActPng, maskOverlay=whiteMatterAct, boundaries=whiteMatterAct)



    def __createRegionMaskFromAparcAseg(self, source, operand):

        option = "{}_seeds".format(operand)
        self.info("Extract {} regions from {} image".format(operand, source))
        regions = util.arrayOfInteger(self.get( option))
        self.info("Regions to extract: {}".format(regions))

        target = self.buildName(source, [operand, "extract"])
        structures = mriutil.extractStructure(regions, source, target)
        self.__createMask(structures)

    """
    def __actAnatPrepareFreesurfer(self, source):
        target = self.buildName(source, 'act')
        freesurfer_lut = os.path.join(os.environ['FREESURFER_HOME'], 'FreeSurferColorLUT.txt')

        if not os.path.isfile(freesurfer_lut):
          self.error("Could not find FreeSurfer lookup table file: Expected location: {}".format(freesurfer_lut))

        config_path = os.path.join(self.toadDir, "templates", "lookup_tables", "FreeSurfer2ACT.txt");
        if not os.path.isfile(config_path):
          self.error("Could not find config file for converting FreeSurfer parcellation output to tissues: Expected location: {}".format(config_path))

        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initial conversion from FreeSurfer parcellation to five principal tissue types
        self.launchCommand('labelconfig -quiet ' + source + ' ' + config_path + ' ' + os.path.join(temp_dir, 'indices.mif') + ' -lut_freesurfer ' + freesurfer_lut)

        # Convert into the 5TT format for ACT
        mriutil.mrcalc('indices.mif','1','cgm.mif')
        mriutil.mrcalc('indices.mif','2','sgm.mif')
        mriutil.mrcalc('indices.mif','3','wm.mif')
        mriutil.mrcalc('indices.mif','4','csf.mif')
        mriutil.mrcalc('indices.mif','5','path.mif')

        result_path = 'result.nii.gz'
        self.launchCommand('mrcat cgm.mif sgm.mif wm.mif csf.mif path.mif -quiet - -axis 3' + ' | mrconvert - ' + result_path + ' -datatype float32 -quiet')


        # Move back to original directory
        os.chdir(self.workingDir)

        # Get the final file from the temporary directory & put it in the correct location
        shutil.move(os.path.join(temp_dir, result_path), target)

        # Don't leave a trace
        shutil.rmtree(temp_dir)

        return target
        """


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
        return Images((self.getImage(self.dependDir,"aparc_aseg", "resample"), 'resampled parcellation'),
                    (self.getImage(self.dependDir,"aparc_aseg", "register"), 'register parcellation'),
                    (self.getImage(self.dependDir,'mask', 'resample'),  'brain extracted, resampled high resolution'),
                    (self.getImage(self.dependDir,'mask', 'register'),  'brain extracted, register high resolution'),
                    (self.getImage(self.dependDir,'tt5', 'resample'),  '5tt resample'),
                    (self.getImage(self.dependDir,'tt5', 'register'),  '5tt register'))

    def isDirty(self):
        images = Images((os.path.join(self.workingDir, 'FreeSurferColorLUT_ItkSnap.txt'), 'freesurfer color look up table'),
                     (self.getImage(self.workingDir, 'aparc_aseg',['253','mask']), 'area 253 from aparc_aseg'),
                     (self.getImage(self.workingDir, 'aparc_aseg',['1024','mask']), 'area 1024 from aparc_aseg'),
                     (self.getImage(self.workingDir, "tt5", ["resample", "wm", "mask"]), 'resample white segmented mask'),
                     (self.getImage(self.workingDir, "tt5", ["register", "5tt2gmwmi"]), 'grey matter, white matter interface'))

        if self.get("start_seeds").strip() != "":
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'start', 'extract', 'mask']), 'high resolution, start, brain extracted mask'))
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'start', 'extract']), 'high resolution, start, brain extracted'))

        if self.get("stop_seeds").strip() != "":
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'stop', 'extract', 'mask']), 'high resolution, stop, brain extracted mask'))
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'stop', 'extract']), 'high resolution, stop, brain extracted'))

        if self.get("exclude_seeds").strip() != "":
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'exclude', 'extract', 'mask']), 'high resolution, excluded, brain extracted, mask'))
            images.append((self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'exclude', 'extract']), 'high resolution, excluded, brain extracted'))

        return images

    def qaSupplier(self):
        return Images(
            (self.getImage(self.workingDir, "tt5", ["register", "5tt2gmwmi"], ext='png'), 'Grey matter, white matter interface'),
            (self.getImage(self.workingDir, "tt5", ["resample", "wm", "mask"], ext='png'), 'Resample white segmented mask'),
            )

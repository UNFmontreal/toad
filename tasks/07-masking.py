from lib.generictask import GenericTask
from lib import util, mriutil
import tempfile
import shutil
import sys
import os

__author__ = 'desmat'


class Masking(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'registration')


    def implement(self):
        aparcAsegResample = self.getImage(self.dependDir,"aparc_aseg", "resample")
        aparcAsegRegister = self.getImage(self.dependDir,"aparc_aseg", "register")
        anatBrainResample = self.getImage(self.dependDir,'anat', ['brain','resample'] )
	print aparcAsegResample
	print aparcAsegRegister
	print anatBrainResample
        #anatBrainWMResample = self.getImage(self.dependDir, 'anat', ['brain','wm','resample'])
        #self.__createMask(anatBrainWMResample)

        extended = self.buildName('anat', 'extended')
        self.info("Add {} and {} images together in order to create the ultimate image"
                  .format(anatBrainResample, aparcAsegResample))
        mriutil.fslmaths(anatBrainResample, extended, 'add', aparcAsegResample)
        self.__createMask(extended)
        self.__createMask(aparcAsegResample)

        #produce optionnal mask
        if self.get("start_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'start')
        if self.get("stop_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'stop')
        if self.get("exclude_seeds").strip():
            self.__createRegionMaskFromAparcAseg(aparcAsegResample, 'exclude')

        #Launch act_anat_prepare_freesurfer
        actRegister = self.__actAnatPrepareFreesurfer(aparcAsegRegister)
        actResample = self.__actAnatPrepareFreesurfer(aparcAsegResample)

        #extract the white matter mask from the act
        whiteMatterAct = self.__extractWhiteMatterFromAct(actResample)

        #Produces a mask image suitable for seeding streamlines from the grey matter - white matter interface
        seed_gmwmi = self.__launch5tt2gmwmi(actRegister)

        colorLut = "{}/templates/lookup_tables/FreeSurferColorLUT_ItkSnap.txt".format(self.toadDir)
        self.info("Copying {} file into {}".format(colorLut, self.workingDir))
        shutil.copy(colorLut, self.workingDir)


    def __createRegionMaskFromAparcAseg(self, source, operand):

        option = "{}_seeds".format(operand)
        self.info("Extract {} regions from {} image".format(operand, source))
        regions = util.arrayOfInteger(self.get( option))
        self.info("Regions to extract: {}".format(regions))

        target = self.buildName(source, [operand, "extract"])
        structures = mriutil.extractFreesurferStructure(regions, source, target)
        self.__createMask(structures)


    def __actAnatPrepareFreesurfer(self, source):

        sys.path.append(os.environ["MRTRIX_PYTHON_SCRIPTS"])
        target = self.buildName(source, 'act')
        freesurfer_lut = os.path.join(os.environ['FREESURFER_HOME'], 'FreeSurferColorLUT.txt')

        if not os.path.isfile(freesurfer_lut):
          self.error("Could not find FreeSurfer lookup table file: Expected location: {}".format(freesurfer_lut))

        config_path = os.path.join(os.environ["MRTRIX_PYTHON_SCRIPTS"], 'data', 'FreeSurfer2ACT.txt');
        if not os.path.isfile(config_path):
          self.error("Could not find config file for converting FreeSurfer parcellation output to tissues: Expected location: {}".format(config_path))

        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)

        # Initial conversion from FreeSurfer parcellation to five principal tissue types
        self.launchCommand('labelconfig ' + source + ' ' + config_path + ' ' + os.path.join(temp_dir, 'indices.mif') + ' -lut_freesurfer ' + freesurfer_lut)

        # Convert into the 5TT format for ACT
        self.launchCommand('mrcalc indices.mif 1 -eq cgm.mif')
        self.launchCommand('mrcalc indices.mif 2 -eq sgm.mif')
        self.launchCommand('mrcalc indices.mif 3 -eq  wm.mif')
        self.launchCommand('mrcalc indices.mif 4 -eq csf.mif')
        self.launchCommand('mrcalc indices.mif 5 -eq path.mif')
        result_path = 'result.nii.gz'
        self.launchCommand('mrcat cgm.mif sgm.mif wm.mif csf.mif path.mif - -axis 3' + ' | mrconvert - ' + result_path + ' -datatype float32')


        # Move back to original directory
        os.chdir(self.workingDir)

        # Get the final file from the temporary directory & put it in the correct location
        shutil.move(os.path.join(temp_dir, result_path), target)

        # Don't leave a trace
        shutil.rmtree(temp_dir)

        return target


    def __extractWhiteMatterFromAct(self, source):
        """Extract the white matter part from the act

        Args:
            An act image

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

        tmp = os.path.join(self.workingDir, "tmp.nii")
        target = self.buildName(source, "5tt2gmwmi")
        self.info("Starting 5tt2gmwmi creation from mrtrix on {}".format(source))

        cmd = "5tt2gmwmi {} {} -nthreads {} -quiet".format(source, tmp, self.getNTreadsMrtrix())
        self.launchCommand(cmd)

        return self.rename(tmp, target)


    def __createMask(self, source):
        self.info("Create mask from {} images".format(source))
        mriutil.fslmaths(source, self.buildName(source, 'mask'), 'bin')


    def meetRequirement(self):

        images = {'resampled parcellation':self.getImage(self.dependDir,"aparc_aseg", "resample"),
                    'register parcellation':self.getImage(self.dependDir,"aparc_aseg", "register"),
                    'brain extracted, resampled high resolution':self.getImage(self.dependDir,'anat',['brain','resample'])}

        return self.isAllImagesExists(images)


    def isDirty(self, result = False):
        images ={'register anatomically constrained tractography': self.getImage(self.workingDir, "aparc_aseg", ["register", "act"]),
                    'aparc_aseg mask': self.getImage(self.workingDir,"aparc_aseg", ["resample", "mask"]),
                    'ultimate extended mask': self.getImage(self.workingDir, 'anat',['extended', 'mask']),
                    'seeding streamlines 5tt2gmwmi': self.getImage(self.workingDir, "aparc_aseg", "5tt2gmwmi"),
                    'freesurfer color look up table': os.path.join(self.workingDir, 'FreeSurferColorLUT_ItkSnap.txt'),
                    'resample white segmented act mask': self.getImage(self.workingDir,"aparc_aseg", ["resample", "act", "wm", "mask"])
        }

        if self.config.get('masking', "start_seeds").strip() != "":
            images['high resolution, start, brain extracted mask'] = self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'start', 'extract', 'mask'])
            images['high resolution, start, brain extracted'] = self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'start', 'extract'])

        if self.config.get('masking', "stop_seeds").strip() != "":
            images['high resolution, stop, brain extracted mask'] = self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'stop', 'extract', 'mask'])
            images['high resolution, stop, brain extracted'] = self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'stop', 'extract'])

        if self.config.get('masking', "exclude_seeds").strip() != "":
            images['high resolution, excluded, brain extracted, mask'] = self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'exclude', 'extract', 'mask'])
            images['high resolution, excluded, brain extracted']= self.getImage(self.workingDir, 'aparc_aseg', ['resample', 'exclude', 'extract'])

        if self.isSomeImagesMissing(images):
            result = True

        return result


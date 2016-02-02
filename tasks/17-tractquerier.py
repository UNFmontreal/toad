# -*- coding: utf-8 -*-
from core.toad.generictask import GenericTask
from lib import mriutil, util


class Tractquerier(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
                self, subject,
                'backup', 'upsampling', 'registration', 'atlasregistration',
                'tractographymrtrix', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True

    def implement(self):

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Load tractography
        if nbDirections <= 45:
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'
        tractographyTrk = self.getTractographymrtrixImage(
                'dwi', postfixTractography, 'trk')

        ### Get atlas to refere to
        atlasResample = self.__getAtlas()

        ### Find dictionnary
        qryDict = self.__getTractquerierFile('tq_dict', 'qryDict')

        ### Find query
        qryFile = self.__getTractquerierFile('query', 'qryFile')

        # Launch tract_querier
        self.__tractQuerier(tractographyTrk, atlasResample, qryDict, qryFile)

        self.dirty = False


    def __getAtlas(self):
        atlas = self.get('atlas')
        target = self.getAtlasRegistrationImage(atlas, 'resample')
        if not target:
            target = self.getRegistrationImage(atlas, 'resample')
        else:
            print "No atlas resample found in tractquerier task"
        return target


    def __getTractquerierFile(self, prefix, defaultFile):
        target = self.getBackupImage(prefix, None, 'qry')
        if target:
            util.symlink(target, self.buildName(target, None, 'qry'))
        else:
            defaultFileName = self.get(defaultFile)
            defaultFileLink = os.path.join(
                    self.toadDir,
                    "templates",
                    "tract_queries",
                    defaultFileName,
                    )
            target = defaultFileLink
            util.copy(defaultFileLink, self.workingDir, self.get(defaultFile))
        return target


    def __tractQuerier(self, trk, atlas, qryDict, qryFile):
        target = self.buildName(trk, None, 'trk')
        cmd = "tract_querier -t {} -a {} -I {} -q {} -o {}"
        cmd = cmd.format(trk, atlas, qryDict, qryFile, target)
        self.launchCommand(cmd)
        return target


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """
        return True

    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        return self.dirty

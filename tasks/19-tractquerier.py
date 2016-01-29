# -*- coding: utf-8 -*-
import os.path
from core.toad.generictask import GenericTask
from lib import mriutil, util


class Tractquerier(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(
                self, subject,
                'upsampling', 'registration', 'tractographymrtrix', 'qa')
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

        ### Find query
        if os.path.exists(self.getBackupImage(None, 'query', 'qry')):
            util.symlink() ### Create symlink
        else:
            util.copy(os.path.join(self.toadDir, "templates", "tract_queries", self.get("qryDict")), self.workingDir)

        ### Find dictionnary
        if os.path.exists(self.getBackupImage(None, 'dict', 'qry')):
            util.symlink() ### Create symlink
        else:
            util.copy(os.path.join(self.toadDir, "templates", "tract_queries", self.get("qryFile")), self.workingDir)

        qryFile = self.getTractQuerierImage(None, 'query', 'qry')
        qryDict = self.getTractQuerierImage(None, 'dict', 'qry')


        ### Get atlas to refere to
        if os.path.exists(self.getAtlasRegistrationImage(self.get('atlas'),'resample')):
            atlasResample = self.getAtlasRegistrationImage(self.get('atlas'),'resample')
        else:
            atlasResample = self.getRegistrationImage(self.get('atlas'),'resample')

        self.__tractQuerier(tractographyTrk, atlasResample, qryDict, qryFile)

        self.dirty = False


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

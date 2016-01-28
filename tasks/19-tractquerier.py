# -*- coding: utf-8 -*-
import os.path
from core.toad.generictask import GenericTask
from lib import mriutil


class Tractquerier(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'upsampling', 'registration', 'tractographymrtrix', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True


    def implement(self):

        dwi = self.getUpsamplingImage('dwi', 'upsample')

        self.__nbDirections = mriutil.getNbDirectionsFromDWI(dwi)

        # Load tractography
        if self.__nbDirections <= 45:
            tractographyTrk = self.getTractographymrtrixImage('dwi', 'tensor_prob', 'trk')
        else:
            tractographyTrk = self.getTractographymrtrixImage('dwi', 'hardi_prob', 'trk')

        atlasResample = self.getRegistrationImage('wm', 'resample')


        # tract_querier

        qryFile = os.path.join(self.toadDir, "templates", "tract_queries", self.get("qryFile"))
        qryDict = os.path.join(self.toadDir, "templates", "tract_queries", self.get("qryDict"))

        self.__tractQuerier(tractographyTrk, atlasResample, qryDict, qryFile)

        self.dirty = False

    def __tractQuerier(self, trk, atlas, qryDict, qryFile):

        output = self.buildName(trk, None, 'trk')

        cmd = "tract_querier -t {} -a {} -I {} -q {} -o {}"
        cmd = cmd.format(trk, atlas, qryDict, qryFile, output)
        self.launchCommand(cmd)


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

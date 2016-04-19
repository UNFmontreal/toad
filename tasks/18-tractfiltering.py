# -*- coding: utf-8 -*-
import os
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class TractFiltering(GenericTask):
    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'tractquerier', 'qa')
        self.setCleanupBeforeImplement(False)
        self.dirty = True

    def implement(self):

        im =  self.getTractQuerierImages('dwi', None, 'trk')
        print 'allo'
        print im
        #mriutil.setWorkingDirTractometry(self.workingDir,
        #                                 self.getTractQuerierImages('dwi', None, 'trk'))


        #self._trkAnalysed = self.getTractQuerierImage(None, None, 'trk')


        #mriutil.runTractometry(configTractometry, filteredTractographies, self.workingDir)

    def isIgnore(self):
        return self.get("ignore")

    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """

        #images = Images()

        #Images((self.getTractQuerierImage(None, None, 'trk'),'Tractography files'))

        return True

    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """

        return True

#    def qaSupplier(self):
#        """Create and supply images for the report generated by qa task

#        """
#        qaImages = Images()

#       information = "Warning: due to storage restriction, streamlines were " \
#                      "downsampled. Even if there is no difference in structural " \
#                      "connectivity, you should be careful before computing any " \
#                      "metrics along these streamlines.\n To run toad without this " \
#                      "downsampling, please refer to the documentation."
#        qaImages.setInformation(information)


#        return qaImages

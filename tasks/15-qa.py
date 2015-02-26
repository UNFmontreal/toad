from lib.generictask import GenericTask
import shutil
from lib import util


__author__ = 'cbedetti'

class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject)
        #self.setCleanupBeforeImplement(False)


    def implement(self):
        shutil.copyfile(os.path.join(self.toadDir, "templates/files/qa.main.tpl"), 'index.html')
        


    def meetRequirement(self, result=True):
        """
        
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return self.dirty

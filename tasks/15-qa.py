from lib.generictask import GenericTask
import os
import shutil
from lib import util


__author__ = 'cbedetti'

class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject)
        #self.setCleanupBeforeImplement(False)


    def implement(self):
        if not os.path.exists('img'):
            os.makedirs('img')
        shutil.copyfile(os.path.join(self.toadDir, 'templates/files/logo.png'), 'img/logo.png')
        htmlCode = self.parseTemplate({'parseHtmlTables':''}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))
        util.createScript('index.html', htmlCode)
        

    def meetRequirement(self, result=True):
        """
        
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        files = {'QA index.html': 'index.html', 'toad logo': 'img/logo.png'}
        return self.isSomeImagesMissing(files)

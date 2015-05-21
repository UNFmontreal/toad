import os
import shutil
from core.generictask import GenericTask
from core.tasksmanager import TasksManager
from lib.images import Images
from lib import util


__author__ = 'cbedetti'

class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject)
        self.setCleanupBeforeImplement(False)
        self.__subject = subject

    def implement(self):

        mainTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.main.tpl')
        imagesDir = os.path.join(self.workingDir, self.config.get('qa', 'images_dir'))

        #make image directory
        if not os.path.exists(imagesDir):
            os.makedirs(imagesDir)

        #Create menu links only for tasks with implemented QA
        menuHtml = ""
        qaTasksList = [task.getName() for task in sorted(self.tasksAsReferences) if "qaSupplier" in dir(task)]
        for taskName in qaTasksList:
            menuHtml +="\n<li><a id=\"{0}\" href=\"{0}.html\">{0}</a></li>".format(taskName)

        #Create temporary html for each task
        message = "Task is being processed. Refresh to check completion."
        for name in qaTasksList:
            htmlTaskFileName = "{}.html".format(name)
            if not os.path.exists(htmlTaskFileName):
                tags = {'subject':self.__subject.getName(), 'menuHtml':menuHtml, 'taskInfo':'', 'parseHtmlTables':message}
                htmlCode = self.parseTemplate(tags, mainTemplate)
                util.createScript(htmlTaskFileName, htmlCode)

        #Change denoising html if user is not running this step
        if self.config.get('denoising', 'algorithm').lower() in "none":
            htmlTaskFileName = "denoising.html"
            tags = {'subject':self.__subject.getName(), 'menuHtml':menuHtml, 'taskInfo':'', 'parseHtmlTables':'Step skipped by the user'}
            htmlCode = self.parseTemplate(tags, mainTemplate)
            util.createScript(htmlTaskFileName, htmlCode)

        #Create template specific to the subject
        tags = {'subject':self.__subject.getName(), 'menuHtml':menuHtml}
        htmlCode = self.parseTemplate(tags, mainTemplate)
        util.createScript('qa.main.tpl', htmlCode)

        #Create index.html
        tags = {'subject':self.__subject.getName(), 'menuHtml':menuHtml, 'taskInfo':'', 'parseHtmlTables':''}
        htmlCode = self.parseTemplate(tags, mainTemplate)
        util.createScript('index.html', htmlCode)


    def meetRequirement(self, result=True):
        """
        
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images((os.path.join(self.workingDir, 'index.html'), 'QA index.html')).isSomeImagesMissing()

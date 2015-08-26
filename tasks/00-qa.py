import os
from core.generictask import GenericTask
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
        imagesDir = os.path.join(self.workingDir, self.get('qa', 'images_dir'))

        if not os.path.exists(imagesDir):
            os.makedirs(imagesDir)

        #Create menu links only for tasks with implemented QA
        menuHtml = ""
        menuLinkTemplate = "\n<li><a id=\"{0}\" href=\"{0}.html\">{0}</a></li>"
        qaTasksList = []

        for task in sorted(self.tasksAsReferences):
            if "qaSupplier" in dir(task):
                qaTasksList.append(task.getName())

        for taskName in qaTasksList:
            menuHtml += menuLinkTemplate.format(taskName)

        #Create temporary html for each task
        message = "Task is being processed. Refresh to check completion."
        for taskName in qaTasksList:
            htmlTaskFileName = "{}.html".format(taskName)
            if not os.path.exists(htmlTaskFileName):
                tags = {
                    'subject':self.__subject.getName(),
                    'menuHtml':menuHtml,
                    'taskInfo':'',
                    'parseHtmlTables':message,
                    }
                htmlCode = self.parseTemplate(tags, mainTemplate)
                util.createScript(htmlTaskFileName, htmlCode)

        #Create template specific to the subject
        tags = {
            'subject':self.__subject.getName(),
            'menuHtml':menuHtml,
            }
        htmlCode = self.parseTemplate(tags, mainTemplate)
        util.createScript(self.get('qa', 'subject_template'), htmlCode)

        #Create index.html
        tags = {
            'subject':self.__subject.getName(),
            'menuHtml':menuHtml,
            'taskInfo':'',
            'parseHtmlTables':'',
            }
        htmlCode = self.parseTemplate(tags, mainTemplate)
        util.createScript('index.html', htmlCode)


    def meetRequirement(self, result=True):
        """
        
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images((os.path.join(self.workingDir, 'index.html'), 'QA index.html'))

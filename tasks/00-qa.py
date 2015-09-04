# -*- coding: utf-8 -*-
import os

from core.toad.generictask import GenericTask
from lib.images import Images
from lib import util


__author__ = "Christophe Bedetti"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Christophe Bedetti","Mathieu Desrosiers"]


class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'backup')
        self.setCleanupBeforeImplement(False)
        self.__subject = subject

    def implement(self):

        mainTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.main.tpl')
        imagesDir = os.path.join(self.workingDir, self.get('qa', 'images_dir'))

        if not os.path.exists(imagesDir):
            os.makedirs(imagesDir)

        #Copy style.css
        styleTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.style.tpl')
        util.copy(styleTemplate, self.workingDir, 'style.css')

        #Create menu.html only for tasks with implemented QA
        menuTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.menu.tpl')
        util.copy(menuTemplate, self.workingDir, 'menu.html')

        #Create index.html
        listDir = os.listdir(self.backupDir)
        listDirHtml = 'Input files:<ul>'
        for f in listDir:
            listDirHtml += '<li>{}</li>\n'.format(f)
        listDirHtml += '</ul>'
        tags = {
            'subject':self.__subject.getName(),
            'taskInfo':'',
            'parseHtmlTables':listDirHtml,
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

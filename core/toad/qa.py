# -*- coding: utf-8 -*-
import os
import shutil
import xml.dom.minidom as minidom
from lib import qautil
from lib import util

__author__ = "Christophe Bedetti"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Christophe Bedetti", "Mathieu Desrosiers"]

class Qa(object):

    def __init__(self):
        self.imageFormat = 'jpg'


    def plot3dVolume(self, source):
        """
        Wrapper of the class Plot3dVolume of qautil
        """
        target = self.buildName(source, None, ext=self.imageFormat)
        qaPlot = qautil.Plot3dVolume(source)
        qaPlot.save(target)
        #lut = self.config.get('template', 'freesurfer_lut')
        #lutFiles = os.path.join(self.toadDir, 'templates', 'lookup_tables', lut)
        return target


    def plot4dVolume(self, source):
        """
        Wrapper of the class Plot4dVolume of qautil
        """
        target = self.buildName(source, None, ext='gif')
        qaPlot = qautil.Plot4dVolume(source)
        qaPlot.save(target)
        return target


    def createQaReport(self, images):
        """create html report for a task with qaSupplier implemented
        Args:
           images : an Images object
        """
        mainTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.main.tpl')
        tableTemplate = os.path.join(self.toadDir, 'templates', 'files', 'qa.table.tpl')
        subjectName = self.subject.getName()
        taskInfo = images.getInformation()
        imagesDir = os.path.join(self.qaDir, self.config.get('qa', 'images_dir'))
        versions = minidom.parse(os.path.join(self.logDir, self.get('general','versions_file_name')))
        tablesCode = ''
        
        print "createQaReport images =", images
        for imageLink, legend in images:
            if imageLink:
                path, filename =  os.path.split(imageLink)
                classType = 'large_view'
                if any(_ in filename for _ in ['_translations', '_rotations', '_vectors', '_sigma', '_hist', '_snr', '_ellipsoids']):
                    classType = 'small_view'
                shutil.copyfile(imageLink, os.path.join(imagesDir, filename))
                relativeLink = os.path.join(self.config.get('qa', 'images_dir'), filename)
                tags = {
                    'imageLink':relativeLink,
                    'legend':legend,
                    'class':classType,
                    }
                tablesCode += self.parseTemplate(tags, tableTemplate)
            else:
                tags = {'imageLink':'', 'legend':legend}
                tablesCode += self.parseTemplate(tags, tableTemplate)

        tags = {
            'subject':subjectName,
            'taskInfo':taskInfo,
            'parseHtmlTables':tablesCode,
            'parseVersionTables': versions.toprettyxml(),
            }
        htmlCode = self.parseTemplate(tags, mainTemplate)
        htmlFile = os.path.join(self.qaDir,'{}.html'.format(self.getName()))
        util.createScript(htmlFile, htmlCode)



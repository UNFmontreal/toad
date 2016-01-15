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
        self.qaImagesFormat = self.config.get('qa', 'images_format')
        self.qaImagesDir = os.path.join(
                self.qaDir, self.config.get('qa', 'images_dir'), self.getName())
        self.qaHtmlTemplate = os.path.join(
                self.toadDir, 'templates', 'files',
                self.config.get('qa', 'index_template'))
        self.qaHtml = os.path.join(
                self.qaDir, '{}.html'.format(self.getName()))


    def plot3dVolume(
            self, source, edges=None, segOverlay=None,
            fov=None, colorbar=False, vmax=None, postfix=None):
        """
        Wrapper of the class Plot3dVolume of qautil
        """
        target = self.buildName(source, postfix, ext=self.qaImagesFormat)
        qaPlot = qautil.Plot3dVolume(
                source, fov=fov, colorbar=colorbar, vmax=vmax)
        if segOverlay != None:
            lut = self.config.get('template', 'freesurfer_lut')
            lutFiles = os.path.join(
                    self.toadDir, 'templates', 'lookup_tables', lut)
            qaPlot.setSegOverlay(segOverlay, lutFiles)
            target = self.buildName(segOverlay, None, ext=self.qaImagesFormat)
        if edges !=None:
            qaPlot.setEdges(edges)
            target = self.buildName(edges, None, ext=self.qaImagesFormat)
        qaPlot.save(target)
        return target


    def plot4dVolume(self, source, fov=None):
        """
        Wrapper of the class Plot4dVolume of qautil
        """
        target = self.buildName(source, None, ext='gif')
        qaPlot = qautil.Plot4dVolume(source, fov=fov)
        qaPlot.save(target)
        return target


    def compare4dVolumes(self, source1, source2, fov=None):
        """
        Wrapper of the class Plot4dVolume of qautil
        """
        target = self.buildName(source1, 'compare', ext='gif')
        qaPlot = qautil.Plot4dVolume(source1, source2=source2, fov=fov)
        qaPlot.save(target)
        return target


    def plotMovement(self, parametersFile, basename):
        """
        """
        targetTranslations = self.buildName(
                basename, 'translations', ext=self.qaImagesFormat)
        targetRotations = self.buildName(
                basename, 'rotations', ext=self.qaImagesFormat)
        qautil.plotMovement(
                parametersFile, targetTranslations, targetRotations)
        return targetTranslations, targetRotations


    def plotVectors(self, bvecsFile, bvecsCorrected, basename):
        """
        """
        target = self.buildName(basename, 'vectors', ext='gif')
        qautil.plotVectors(bvecsFile, bvecsCorrected, target)
        return target


    def plotSigma(self, sigma, basename):
        """
        """
        target = self.buildName(basename, 'sigma', ext=self.qaImagesFormat)
        qautil.plotSigma(sigma, target)
        return target


    def noiseAnalysis(self, source, maskNoise, maskCc):
        """
        """
        targetSnr = self.buildName(source, 'snr', ext=self.qaImagesFormat)
        targetHist = self.buildName(source, 'hist', ext=self.qaImagesFormat)
        qautil.noiseAnalysis(source, maskNoise, maskCc, targetSnr, targetHist)
        return targetSnr, targetHist


    def plotReconstruction(self, data, mask, cc, model, basename):
        """
        """
        target = self.buildName(basename, model, ext=self.qaImagesFormat)
        qautil.plotReconstruction(data, mask, cc, target, model)
        return target


    def plotTrk(self, source, anatomical, roi):
        """
        """
        target = self.buildName(source, None, ext=self.qaImagesFormat)
        qautil.plotTrk(source, target, anatomical, roi)
        return target


    def createTaskHtml(self, tags, htmlLink=None):
        """
        Create html file for the task
        Arg:
            tags: dict with the following keys to parse the html template
                subject, taskInfo, taskName, parseHtmlTables, parseVersionTables
                Script fills missing keys
        """
        versions = minidom.parse(os.path.join(
                self.logDir, self.get('general','versions_file_name')))

        if htmlLink == None:
            htmlLink = self.qaHtml

        # Fill missing keys
        baseTags = {
                'jqueryFile': self.config.get('qa', 'jquery'),
                'subject': self.subject.getName(),
                'taskName': self.getName(),
                'taskInfo': '',
                'parseHtmlTables': '',
                'parseVersionTables': versions.toprettyxml()
                }
        for key, value in baseTags.iteritems():
            if not tags.has_key(key): tags[key] = value

        # Parse template and create html file
        htmlCode = self.parseTemplate(tags, self.qaHtmlTemplate)
        util.createScript(htmlLink, htmlCode)


    def updateQaMenu(self):
        """
        This method runs at the beginning of a task with qaSupplier implemented
        It adds a link to the task in qa menu
        """
        taskName = self.getName()
        menuFile = os.path.join(self.qaDir, self.config.get('qa', 'menu'))
        menuLinkTemplate = \
                '<li><a id="{0}" href="{0}.html" target="_top">{0}</a></li>\n'

        #Add task link in qa menu if not already present
        with open(menuFile, 'r') as f:
            lines = f.readlines()
        if not any(taskName in line for line in lines):
            lines.insert(-1, menuLinkTemplate.format(taskName))
        with open(menuFile, 'w') as f:
            for line in lines:
                f.write(line)

        #Create temporary html
        message = "Task is being processed. Refresh to check completion."
        self.createTaskHtml({'taskInfo':message})


    def createQaReport(self, images):
        """create html report for a task with qaSupplier implemented
        Args:
           images : an Images object
        """
        # make qa images directory
        if not os.path.exists(self.qaImagesDir):
            os.makedirs(self.qaImagesDir)

        tableTemplate = os.path.join(
                self.toadDir, 'templates', 'files',
                self.config.get('qa', 'table_template'))

        print "createQaReport images =", images

        smallViewTags = [
                '_translations',
                '_rotations',
                '_vectors',
                '_sigma',
                '_hist',
                '_snr',
                '_ellipsoids']
        tablesCode = ''
        for imageLink, legend in images:
            if imageLink:
                path, filename =  os.path.split(imageLink)

                if any(tag in filename for tag in smallViewTags):
                    classType = 'small_view'
                else:
                    classType = 'large_view'

                # Copy images to qa image directory
                # default: 00-qa/images/<task name>
                shutil.copyfile(
                        imageLink,
                        os.path.join(self.qaImagesDir, filename))

                # Relative link to insert in html code
                relativeLink = os.path.join(
                        self.config.get('qa', 'images_dir'),
                        self.getName(),
                        filename)

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
                'taskInfo':images.getInformation(),
                'parseHtmlTables':tablesCode
                }
        self.createTaskHtml(tags)

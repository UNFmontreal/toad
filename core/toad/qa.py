# -*- coding: utf-8 -*-
import os
import shutil
import xml.dom.minidom as minidom
from jinja2 import Environment, FileSystemLoader
from lib import qautil
from lib import util
import bibtexparser

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
        self.bibtex = os.path.join(
                self.toadDir, 'templates',
                self.config.get('qa', 'bibtex'))


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
        Wrapper of the class Plot4dVolume of qautil to create animated gif
        """
        target = self.buildName(source, None, ext='gif')
        frameFormat = ".{}".format(self.qaImagesFormat)
        qaPlot = qautil.Plot4dVolume(source, fov=fov, frameFormat=frameFormat)
        qaPlot.saveGif(target)
        return target

    def compare4dVolumes(self, source1, source2, fov=None):
        """
        Wrapper of the class Plot4dVolume of qautil
        """
        target = self.buildName(source1, 'compare', ext='gif')
        frameFormat = ".{}".format(self.qaImagesFormat)
        qaPlot = qautil.Plot4dVolume(
        source1, source2=source2, fov=fov, frameFormat=frameFormat)
        qaPlot.saveGif(target)
        return target

    def plot4dVolumeToFrames(self, source, fov=None):
        """
        Wrapper of the class Plot4dVolume of qautil to create several images
        """
        frameFormat = ".{}".format(self.qaImagesFormat)
        cgm = self.buildName(source, 'cgm', ext=frameFormat)
        scgm = self.buildName(source, 'scgm', ext=frameFormat)
        wm = self.buildName(source, 'wm', ext=frameFormat)
        csf = self.buildName(source, 'csf', ext=frameFormat)
        pt = self.buildName(source, 'pt', ext=frameFormat)
        targets = [cgm, scgm, wm, csf, pt]
        qaPlot = qautil.Plot4dVolume(source, fov=fov, frameFormat=frameFormat)
        qaPlot.saveFrames(targets)
        return targets

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
        frameFormat = ".{}".format(self.qaImagesFormat)
        qautil.plotVectors(
        bvecsFile, bvecsCorrected, target, frameFormat=frameFormat)
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

    def plotTrk(self, source, anatomical, roi, xSlice, ySlice, zSlice, xRot, yRot, zRot):
        """
        """
        target = self.buildName(source, None, ext=self.qaImagesFormat)
        qautil.plotTrk(source, target, anatomical, roi, xSlice, ySlice, zSlice,xRot, yRot, zRot)
        return target

    def createTaskHtml(self, tags, htmlLink=None):
        """
        Create html file for the task
        Arg:
            tags: dict with the following keys to parse the html template
                subject, taskInfo, taskName, parseHtmlTables, parseVersionTables
                Script fills missing keys
        """
        versions = ''
        if self.getName() == 'qa':
            print self.logDir
            print self.get('general','versions_file_name')
            versions = minidom.parse(os.path.join(
                    self.logDir, self.get('general','versions_file_name')))
            versions = versions.toprettyxml()

        if htmlLink == None:
            htmlLink = self.qaHtml

        # Fill missing keys
        baseTags = {
                'jqueryFile': self.config.get('qa', 'jquery'),
                'subject': self.subject.getName(),
                'taskName': self.getName(),
                'taskInfo': '',
                'parseHtmlTables': '',
                'parseVersionTables': versions,
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


    def createMethoHtml(self):
        templateDir = os.path.join(self.toadDir, 'templates', 'files')
        jinja2Env = Environment(
                loader=FileSystemLoader(templateDir), trim_blocks=True)
        tpl = jinja2Env.get_template('metho.tpl')

        tags_softwares = self.__getVersions()
        tags_metho = self.__getTags(tags_softwares)
        #  print tags_metho
        htmlCode = tpl.render(**tags_metho)
        util.createScript(os.path.join(self.qaDir,'metho.html'), htmlCode)

    def __getVersions(self):
        tags = {}
        versions = minidom.parse(os.path.join(
                    self.logDir, self.get('general','versions_file_name')))
        softs = versions.getElementsByTagName('softwares')[-1].getElementsByTagName('software')

        for soft in softs:
            currentVersion = str(soft.getElementsByTagName('version')[0].firstChild.data)
            currentSoft = str(soft.getElementsByTagName('name')[0].firstChild.data).lower()

            if 'freesurfer' in currentSoft:
                currentVersion = currentVersion.split('pub-')[1]

            tags[ currentSoft + '_vers'] = currentVersion


        return tags

    def configGet(self, section, key):
        try:
            value = self.config.get(section, key)
        except:
            value = None
        return value

    def configFillSection(self, section, withName = False):
        tags = {}
        items = self.config.items(section)

        if withName:
            prefix = section + '_'
        else:
            prefix = ''

        for item in items:
            if item[1].lower() == 'true':
                tags[prefix + item[0]] = True
            elif item[1].lower() == 'false':
                tags[prefix + item[0]] = False
            elif 'voxelsize' in item[0].lower():
                tags[prefix + item[0] + '_1'] = float(item[1].translate(None,'[],').split()[0])
                tags[prefix + item[0] + '_2'] = float(item[1].translate(None,'[],').split()[1])
                tags[prefix + item[0] + '_3'] = float(item[1].translate(None,'[],').split()[2])
                if tags[prefix + item[0] + '_1']==tags[prefix + item[0] + '_2'] and tags[prefix + item[0] + '_1'] == tags[prefix + item[0] + '_2']:
                    tags[prefix + item[0] + '_iso'] = True
                    tags[prefix + item[0]] = tags[prefix + item[0] + '_1']
                else:
                    tags[prefix + item[0] + '_iso'] = False

            elif 'matrixsize' in item[0].lower():
                tags[prefix + item[0] + '_1'] = float(item[1].translate(None,'[],').split()[0])
                tags[prefix + item[0] + '_2'] = float(item[1].translate(None,'[],').split()[0])

            else:
                tags[prefix + item[0]] = item[1]

        return tags

    def __getTags(self, tags_softwares):


        methodology = self.configFillSection('methodology') # Fill tags with config file informations
        denoising = self.configFillSection('denoising', True)
        correction = self.configFillSection('correction', True)
        upsampling = self.configFillSection('upsampling', True)
        tensorfsl = self.configFillSection('tensorfsl', True)
        tensordipy = self.configFillSection('tensordipy', True)
        tensormrtrix = self.configFillSection('tensormrtrix', True)
        hardimrtrix = self.configFillSection('hardimrtrix', True)
        hardidipy = self.configFillSection('hardidipy', True)
        tractographymrtrix = self.configFillSection('tractographymrtrix', True)
        tractquerier = self.configFillSection('tractquerier', True)
        tractfiltering = self.configFillSection('tractfiltering', True)
        tractometry = self.configFillSection('tractometry', True)

        references = self.configFillSection('references')

        tags = util.merge_dicts(methodology, denoising, denoising, correction, upsampling, 
                                tensorfsl, tensordipy, tensormrtrix, hardimrtrix, hardidipy, tractographymrtrix, tractquerier, tractfiltering, tractometry, tags_softwares)

        # Special case for 3T Tim Trio
        if tags['magneticfieldstrength'] == '3' and tags['mrmodel'] == 'TrioTim' and tags['denoising_number_array_coil'] == '4':
            tags['number_array_coil'] = 12
        else:
            tags['number_array_coil'] = tags['denoising_number_array_coil']

        methodology = ''
        bibReferences = []

        indexReferences = 1
        if not tags['denoising_ignore']:
            methodology += 'First, DWI were denoised using {} method [{}]. '.format(tags['denoising_algorithm'],indexReferences)
            if tags['denoising_algorithm'] == 'nlmeans':
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_nlmeans']))
            elif tags['denoising_algorithm'] == 'aonlm':
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_aonlm']))
            elif tags['denoising_algorithm'] == 'lpca':
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_lpca']))
            elif tags['denoising_algorithm'] == 'mp-pca':
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_mppca']))
            indexReferences += 1

        if not tags['correction_ignore']:
            if not tags['denoising_ignore']:
                methodology += 'Then, they were corrected using {} [{}]. '.format(tags['correction_method'],indexReferences)
                methodology +=  'Gradient directions were corrected corresponding to motion correction parameters. '
            else:
                methodology += 'First, DWI were corrected using {} [{}]. '.format(tags['correction_method'],indexReferences)

            methodology += 'Motion-corrected images '

            bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_correction']))
            indexReferences += 1


        else:
            methodology += 'DWI '

        methodology += 'were upsampled using {} interpolation (upsampling to anatomical resolution). '.format(tags['upsampling_interp'])

        methodology += '</ br>Anatomical image went through Freesurfer pipeline [{}] in order to be used in the Anatomically-Constrained Tractography (ACT). T1 image was registered to the DWI '.format(indexReferences)
        bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_freesurfer']))
        indexReferences += 1

        if not (tags['tensorfsl_ignore'] and  tags['tensordipy_ignore'] and tags['tensormrtrix_ignore']):
            methodology += '<p>Eigenvectors, eigenvalues, fractional anisotropy (FA), radial diffusivity (RD), axial diffusivity (AD) and mean diffusivity (MD) were extracted from tensor reconstruction using '
            if not (tags['tensorfsl_ignore'] and  tags['tensordipy_ignore'] and tags['tensormrtrix_ignore']):
                methodology += 'FDT toolbox from FSL {} using {} method [{}] '.format(tags['fsl_vers'], tags['tensorfsl_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensorfsl']))
                indexReferences += 1

                methodology += 'and DIPY {} using {} method [{}] '.format(tags['dipy_vers'], tags['tensordipy_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_dipy']))
                indexReferences += 1

                methodology += 'and MRtrix {} using {} method [{}]. '.format(tags['mrtrix_vers'], tags['tensormrtrix_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensormrtrix']))
                indexReferences += 1

            elif not (tags['tensorfsl_ignore'] and tags['tensordipy_ignore']):
                methodology += 'FDT toolbox from FSL {} using {} method [{}] '.format(tags['fsl_vers'], tags['tensorfsl_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensorfsl']))
                indexReferences += 1

                methodology += 'and DIPY {} using {} method [{}]. '.format(tags['dipy_vers'], tags['tensordipy_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_dipy']))
                indexReferences += 1

            elif not (tags['tensorfsl_ignore'] and tags['tensormrtrix_ignore']):
                methodology += 'FDT toolbox from FSL {} using {} method [{}] '.format(tags['fsl_vers'], tags['tensorfsl_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensorfsl']))
                indexReferences += 1

                methodology += 'and MRtrix {} using {} method [{}]. '.format(tags['mrtrix_vers'], tags['tensormrtrix_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensormrtrix']))
                indexReferences += 1

            elif not (tags['tensordipy_ignore'] and tags['tensormrtrix_ignore']):
                methodology += 'DIPY {} using {} method [{}]. '.format(tags['dipy_vers'], tags['tensordipy_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_dipy']))
                indexReferences += 1

                methodology += 'and MRtrix {} using {} method {}]. '.format(tags['mrtrix_vers'], tags['tensormrtrix_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensormrtrix']))
                indexReferences += 1

            elif not tags['tensorfsl_ignore']:
                methodology += 'FDT toolbox from FSL {} using {} method [{}]. '.format(tags['fsl_vers'], tags['tensorfsl_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensorfsl']))
                indexReferences += 1

            elif not tags['tensordipy_ignore']:
                methodology += 'DIPY {} using {} method [{}]. '.format(tags['dipy_vers'], tags['tensordipy_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_dipy']))
                indexReferences += 1

            elif not tags['tensormrtrix_ignore']:
                methodology += 'MRtrix {} using {} method [{}]. '.format(tags['mrtrix_vers'], tags['tensormrtrix_fitmethod'], indexReferences)
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tensormrtrix']))
                indexReferences += 1

            methodology += '</p>'

        if not (tags['hardidipy_ignore'] or tags['hardimrtrix_ignore']):
            methodology += '<p>Fiber orientation distribution function (fODF) reconstruction was done using '

        if not tags['hardidipy_ignore']:
            methodology += 'DIPY'
            if tags['tensordipy_ignore']:
                methodology += ' {} [{}]'.format(tags['ref_dipy'], indexReferences)

        elif not tags['hardimrtrix_ignore']:
            methodology += 'MRtrix'
            if tags['tensordipy_ignore']:
                methodology += ' {} [{}]'.format(tags['ref_mrtrix'], indexReferences)

        if not (tags['hardimrtrix_ignore'] and tags['hardidipy_ignore']): 
            methodology += ' and MRtrix. '
        else:
            methodology += '. '

        if not tags['hardidipy_ignore']:
            methodology += 'Dipy method: The response function for a single fibre population was estimated using {}. '.format(tags['hardidipy_algorithmresponsefunction'])

            methodology += 'This response function was then used to estimate the FOD for each voxel using Constrained Spherical Deconvolution (CSD) [{}] with a maximum spherical harmonic order lmax of {}. '.format(indexReferences, tags['hardidipy_lmax'])
            bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_hardimrtrix']))
            indexReferences += 1

        if not tags['hardimrtrix_ignore']:
            methodology += 'MRtrix method: The response function for a single fibre population was estimated using {} algorithm [{}]. '.format(tags['hardimrtrix_algorithmresponsefunction'], indexReferences)
            if tags['hardidipy_algorithmresponsefunction'] == 'tournier':
                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_estimationResponseTournier']))
                indexReferences += 1
            if tags['hardidipy_ignore']:
                methodology += 'This response function was then used to estimate the FOD for each voxel using Constrained Spherical Deconvolution (CSD) [{}] with a maximum spherical harmonic order lmax of {}. '.format(indexReferences, tags['hardimrtrix_lmax'])

                bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_hardimrtrix']))
                indexReferences += 1
            else:
                methodology += 'This response function was then used to estimate the FOD for each voxel using Constrained Spherical Deconvolution (CSD) [{}] with a maximum spherical harmonic order lmax of {}. '.format(indexReferences-1, tags['hardimrtrix_lmax'])

        if not (tags['hardidipy_ignore'] or tags['hardimrtrix_ignore']):
            methodology += '</p>'

        if not tags['tractographymrtrix_ignore']:
            methodology += '<p>{} tractography was performed using ACT [{}] algorithm. Tractogram of {} streamlines was generated. Any track with length > {} mm was discarded. Because of storage restriction we had to downsample streamlines to a factor of {}. '.format(tags['tractographymrtrix_algorithm'], indexReferences, tags['tractographymrtrix_numbertracks'], tags['tractographymrtrix_maxlength'], tags['tractographymrtrix_downsample'])

            bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tractomrtrix']))
            indexReferences += 1

        if not tags['tractquerier_ignore']:
            methodology += 'Then, we used White Matter Query Language [{}] to select bundles of interest. '.format(indexReferences)
            bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tractquerier']))
            indexReferences += 1

        if not tags['tractfiltering_ignore']:
            methodology += 'These bundles have been filtered to remove outliers streamlines [{}]. '.format(indexReferences)

        if not tags['tractometry_ignore']:
            methodology += '<p>Finally, we use metrics from reconstruction method (HARDI and Tensor) to get these metrics along the streamlines.'.format(indexReferences-1)
            bibReferences.append("<p>[%s] %s</p></ br>" % (indexReferences, references['ref_tractometry']))
            indexReferences += 1


        tags['methodology'] = methodology

        allRefs = ''
        for ref in bibReferences:
            allRefs = allRefs + '\n' + ref

        tags['allReferences'] = allRefs

        return tags


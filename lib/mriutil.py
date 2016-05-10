# -*- coding: utf-8 -*-
import nibabel
import random
import scipy
import numpy
import util
import os
from shutil import rmtree
from collections import OrderedDict

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


def fslmaths(source1, target, operator="bin", source2=None):
    """Perform a mathematical operations using a second image or a numeric value

    Args:
        source1: he input image
        target:  Name of the resulting output image
        operator: Operator to apply
        source2: Image associate with the operator if Binary operation is specified

    Returns:
        A tuple of 3 elements representing (the command launch, the stdout and stderr of the execution)

    """
    if source2 is None:
        cmd = "fslmaths {} -{} {} ".format(source1, operator, target)
    else:
        cmd = "fslmaths {} -{} {} {}".format(source1, operator, source2, target)

    return util.launchCommand(cmd)


def extractFirstB0FromDwi(source, target, bVals, nthreads = "1"):
    """Perform an extraction of the first b0 image found into a DWI image

    Args:
        source: The input image
        target: The resulting output name
        bvals:   A gradient encoding B0 values file name

    Returns:
         A tuple of 3 elements representing (the command launch, the stdout and stderr of the execution)
    """
    return extractSubVolume(source, target, "3", getFirstB0IndexFromDwi(bVals), nthreads)


def extractSubVolume(source, target, extractAtAxis, extractAtCoordinate, nthreads = "1"):
    """Perform an extraction of a subset of the source image

    Args:
        source: The input image
        target: The resulting output name
        extractAtAxis: extract data only in the axis of interest
        extractAtCoordinate: extract data only in the coordinates of interest

    Returns:
         A tuple of 3 elements representing (the command launch, the stdout and stderr of the execution)
    """
    cmd = "mrconvert -coord {} {} {} {} -nthreads {} -quiet".format(extractAtAxis, extractAtCoordinate, source, target, nthreads)
    return util.launchCommand(cmd)


def mrinfo(source):
    """display or extract specific information from the source header.

    Args:
        source: the input image

    Returns:
        An array of information generate by the standard output command line

    Raises:
        ValueError: if mrinfo binary is not found
    """

    cmd = "mrinfo {}".format(source)
    (executedCmd, stdout, stderr) = util.launchCommand(cmd)
    return stdout.splitlines()

def mrcalc(source, value, target):
    """
    #@TODO comment the purpose of this function
    """
    cmd = "mrcalc {} {} -eq {} -quiet".format(source, value, target)
    return util.launchCommand(cmd)


def invertMatrix(source, target):
    """ invert a transformation matrices

    Args:
        source: an input transformation matrices
        target: an output transformation matrices name

    Returns:
        the resulting output transformation matrices name

    """
    cmd = "convert_xfm -inverse {} -omat {}".format(source, target)
    return util.launchCommand(cmd)


def stride3DImage(source, target, layout="1,2,3" ):
    """perform a reorientation of the axes and flip the image into a different layout

    Args:
        source:           the input image
        layout:           comma-separated list that specify the strides.
        outputNamePrefix: a prefix to rename target filename

    Returns:
        A 3 elements tuples representing the command line launch, the standards output and the standard error message
    """
    cmd = "mrconvert {} {} -stride {}".format(source, target, layout)
    return util.launchCommand(cmd)


def __getMrinfoFieldValues(text, field, delimiter=""):
    """Utility function that extract valuable array information from mrinfo metadata
    this function is not portale
    Args:
        text: the data info return by an mrinfo command call
        field: the fieldname to extract values of.
        delimiter: use to split an string elements into array

    Returns:
        an array of elements (strings or float... whatever)

    """
    output = []
    for line in text:
        if field in line:
            if not delimiter:
                return line.replace(field,"").strip()
            else:
                tokens = line.replace(field,"").strip().split("x")

                for token in tokens:
                    try:
                        float(token)
                        output.append(token.strip())
                    except ValueError:
                        pass
    return output


def getMriDimensions(source):
    """get the image dimension along each axis of the source image

    Args:
        source: A mri image

    Returns:
        the image dimension along each axis

    """
    return __getMrinfoFieldValues(mrinfo(source), "Dimensions:", "x")


def getMriVoxelSize(source):
    """get the voxel size of the source image

    Args:
        source: A mri image

    Returns:
        the voxel size of the source image

    """
    return __getMrinfoFieldValues(mrinfo(source), "Voxel size:", "x")


def getNbDirectionsFromDWI(source):
    """get the number of directions contains into the source image

    Args:
        source: A mri image

    Returns:
        the number of directions contains into the source image

    """
    dimensions =  getMriDimensions(source)
    if len(dimensions) == 4:
            return int(dimensions[3])
    return 0


def getDataStridesOrientation(source):
    """ return data stride layout

    Args:
        source: A mri image

    Returns:
        An array of string elements representing the layout of the image

    """
    return ",".join(__getMrinfoFieldValues(mrinfo(source), "Data strides:").strip("[]").split())


def isDataStridesOrientationExpected(source, layouts):
    """Determine if a source image is oriented in the same direction as describe as layouts

    Args:
        source:  A mri image
        layouts: A 3 elements list representing the expected orientation

    Returns:
        A Boolean True if orientation of the dwi image is the same as layouts, False otherwise

    """
    strides = getDataStridesOrientation(source).split(",")
    expectedStrides = layouts.split(",")
    if (len(expectedStrides) == 3) and (len(strides) >= 3):
        if strides[0].strip() in expectedStrides[0] \
                and strides[1].strip() in expectedStrides[1] \
                and strides[2].strip() in expectedStrides[2]:
            return True
    return False


def getFirstB0IndexFromDwi(bVals):
    """Return the index of the first B0 value found into B0 Value encoding file.

    Args:
        bVals:  A B value encoging file

    Returns:
        The index of the first b0 found in the file

    """
    with open(bVals,'r') as f:
        for line in f.readlines():
                b0s = line.strip().split()
                return b0s.index('0')
    return False


def applyGradientCorrection(bFilename, eddyFilename, target):
    """Apply gradient correction to an already existing gradient encoding file.

    Args:
        bFilename: the original gradient encoding file.
        eddyFilename:  corrected gradient file after an eddy correction

    Returns:
        the resulting gradient encoding file

    """
    f = open(eddyFilename, 'r')
    g = open(bFilename, 'r')
    eddys = f.readlines()
    b_line = g.readlines()
    f.close()
    g.close()

    h = open(target, 'w')

    for index, line in enumerate(eddys):
        row_four_to_six_eddy = line.split('  ')[3:6]
        x= numpy.matrix([[1, 0, 0],
                         [0,numpy.cos(float(row_four_to_six_eddy[0])), numpy.sin(float(row_four_to_six_eddy[0]))],
                         [0,-numpy.sin(float(row_four_to_six_eddy[0])), numpy.cos(float(row_four_to_six_eddy[0]))]])

        y= numpy.matrix([[numpy.cos(float(row_four_to_six_eddy[1])), 0, numpy.sin(float(row_four_to_six_eddy[1]))],
                     [0, 1, 0],
                     [-numpy.sin(float(row_four_to_six_eddy[1])), 0, numpy.cos(float(row_four_to_six_eddy[1]))]])

        z= numpy.matrix([[numpy.cos(float(row_four_to_six_eddy[1])), numpy.sin(float(row_four_to_six_eddy[1])), 0],
                     [-numpy.sin(float(row_four_to_six_eddy[1])), numpy.cos(float(row_four_to_six_eddy[1])), 0],
                     [0, 0, 1]])
        matrix = (z*y*x).I
        b_values = b_line[index].split(',')
        gradient = numpy.matrix([[float(b_values[0]), float(b_values[1]),float(b_values[2])]])
        new_gradient = matrix*gradient.T

        values = str(float(new_gradient[0]))+','+str(float(new_gradient[1]))+','+str(float(new_gradient[2]))+','+b_values[3].strip()+'\n'
        h.write(values)

    h.close()
    return target


def fslToMrtrixEncoding(dwi, bVecs, bVals, target):
    """Create a B encoding gradient file base on bVals and bVecs encoding file

    Args:
        dwi:           the input diffusion weight images
        bVecs: a vector value file.
        bVals: a gradient b value encoding file.
        target: the output file name
    Returns:
        A 3 elements tuples representing the command line launch, the standards output and the standard error message

    """
    cmd = "mrinfo {} -fslgrad {} {} -export_grad_mrtrix {} --quiet".format(dwi, bVecs, bVals, target)
    return util.launchCommand(cmd)


def mrtrixToFslEncoding(dwi, bEncs, bVecsTarget, bValsTarget):
    """Create a B encoding gradient file base on bVals and bVecs encoding file

    Args:
        dwi:           the input diffusion weight images
        bEncs: a mrtrix encoding gradient direction file.
        bVecsTarget: a output vector file name.
        bValsTarget: a output value file name.
    Returns:
        A 3 elements tuples representing the command line launch, the standards output and the standard error message

    """
    cmd = "mrinfo {} -grad {} -export_grad_fsl {} {} --quiet".format(dwi, bEncs, bVecsTarget, bValsTarget)
    return util.launchCommand(cmd)


def extractStructure(values, source, target):
    """ Extract givens values from image

    Args:
        values: A list of values (integer) to extract from an input image
        source: An mri image

    returns:
        a new image that contain areas specified by values
    """
    image = nibabel.load(source)
    data = image.get_data()
    c = []
    for value in values:
        c.append(numpy.where(data==value))

    data.fill(0)
    for i in range(len(values)):
        data[c[i]] = 1

    if not os.path.exists(target):
        nibabel.save(nibabel.Nifti1Image(data, image.get_affine()), target)
        return target


def plotConnectome(source, target,  lutFile=None, title=None, label=None, skiprows=0, usecols=None, useGrid=False):
    """ Create a imshow plot

    Args:
        source: an input source file

    Return:
        A png image of the plot

    """
    #ADD figsize

    def __getDataIndexsAndLabels(lutFile):
        """ This need to be implemented

        """
        with open(lutFile, 'r') as f:
            labels = []
            locations = []
            luts = f.readlines()
            if len(luts) == 1:
                labels = luts[0].split()
                #if len(labels) == len(locations):
                for index, label in enumerate(labels):
                    labels.append(label)
                    locations.append(index)
            else:
                for lut in luts:
                    index = int(lut.split()[0])
                    if index != 0:
                    	label = lut.split()[7]
                    	labels.append(label.strip().strip("\""))
                        locations.append(index-1)
        return locations, labels

    import matplotlib.pylab as plt
    data = numpy.loadtxt(source, skiprows=skiprows, usecols=usecols)
    figure = plt.figure(figsize=(18,14), dpi=120)
    #figure.clf()
    ax = figure.add_subplot(111)
    #Connectomme matrix must be square
    if lutFile is not None:
        indexLocations, labels = __getDataIndexsAndLabels(lutFile)

        #probably a better solution exists to reshape the matrix
        data = numpy.take(data, indexLocations, axis=0)
        data = numpy.take(data, indexLocations, axis=1)

    else:
        labels = [index for index in range(data.shape[0])]
 
    image = ax.imshow(data, interpolation="nearest")
    colorBar = plt.colorbar(image)
    plt.setp(colorBar.ax.get_yticklabels(), visible=True)

    plt.xticks([index for index in range(0, len(labels)-1)], labels, rotation='vertical', fontsize=8)
    plt.yticks([index for index in range(0, len(labels)-1)], labels, fontsize=8)
    #plt.subplots_adjust(bottom=0.1, left=0.1, right=1)

    if title is not None:
        plt.title(title)
    if label is not None:
        plt.xlabel(label)
    plt.grid(useGrid)
    figure.savefig(target)
    return target


def transform_to_affine(streams, header, affine):
    from dipy.tracking.utils import move_streamlines
    rotation, scale = numpy.linalg.qr(affine)
    streams = move_streamlines(streams, rotation)
    scale[0:3,0:3] = numpy.dot(scale[0:3,0:3], numpy.diag(1./header['voxel_size']))
    scale[0:3,3] = abs(scale[0:3,3])
    streams = move_streamlines(streams, scale)
    return streams


def read_mrtrix_tracks(in_file, as_generator=True):
    header = read_mrtrix_header(in_file)
    streamlines = read_mrtrix_streamlines(in_file, header, as_generator)
    return header, streamlines


def read_mrtrix_header(in_file):
    fileobj = open(in_file,'r')
    header = {}
    for line in fileobj:
        if line == 'END\n':
            break
        elif ': ' in line:
            line = line.replace('\n','')
            line = line.replace("'","")
            key  = line.split(': ')[0]
            value = line.split(': ')[1]
            header[key] = value
    fileobj.close()
    header['count'] = int(header['count'].replace('\n',''))
    header['offset'] = int(header['file'].replace('.',''))
    return header


def read_mrtrix_streamlines(in_file, header, as_generator=True):
    offset = header['offset']
    stream_count = header['count']
    fileobj = open(in_file,'r')
    fileobj.seek(offset)
    endianness = nibabel.volumeutils.native_code
    f4dt = numpy.dtype(endianness + 'f4')
    pt_cols = 3
    bytesize = pt_cols*4
    def points_per_track(offset):
        track_points = []
        all_str = fileobj.read()
        num_triplets = len(all_str)/bytesize
        pts = numpy.ndarray(shape=(num_triplets,pt_cols), dtype='f4',buffer=all_str)
        nonfinite_list = numpy.where(numpy.isfinite(pts[:,2]) == False)
        nonfinite_list = list(nonfinite_list[0])[0:-1]
        for idx, value in enumerate(nonfinite_list):
            if idx == 0:
                track_points.append(nonfinite_list[idx])
            else:
                track_points.append(nonfinite_list[idx]-nonfinite_list[idx-1]-1)
        return track_points, nonfinite_list

    def track_gen(track_points):
        n_streams = 0
        while True:
            try:
                n_pts = track_points[n_streams]
            except IndexError:
                break
            pts_str = fileobj.read(n_pts * bytesize)
            nan_str = fileobj.read(bytesize)
            if len(pts_str) < (n_pts * bytesize):
                if not n_streams == stream_count:
                    raise StandardError
                break
            pts = numpy.ndarray(
                shape = (n_pts, pt_cols),
                dtype = f4dt,
                buffer = pts_str)
            nan_pt = numpy.ndarray(
                shape = (1, pt_cols),
                dtype = f4dt,
                buffer = nan_str)
            if numpy.isfinite(nan_pt[0][0]):
                raise ValueError
                break
            xyz = pts[:,:3]
            yield xyz
            n_streams += 1
            if n_streams == stream_count:
                raise StopIteration

    track_points, nonfinite_list = points_per_track(offset)
    fileobj.seek(offset)
    streamlines = track_gen(track_points)
    if not as_generator:
        streamlines = list(streamlines)
    return streamlines


def get_data_dims(volume):
    if isinstance(volume, list):
        volume = volume[0]
    nii = nibabel.load(volume)
    hdr = nii.get_header()
    datadims = hdr.get_data_shape()
    return [int(datadims[0]), int(datadims[1]), int(datadims[2])]


def get_vox_dims(volume):
    if isinstance(volume, list):
        volume = volume[0]
    nii = nibabel.load(volume)
    hdr = nii.get_header()
    voxdims = hdr.get_zooms()
    return [float(voxdims[0]), float(voxdims[1]), float(voxdims[2])]


def tck2trk(source, anatomical ,target):
    """ Converts MRtrix (.tck) tract files into TrackVis (.trk) format using functions from dipy

    Args:

        source: an mrtrix tractography file
        anatomical: a high resolution image
        target: an output Trackvis format image

    """
    dx, dy, dz = get_data_dims(anatomical)
    vx, vy, vz = get_vox_dims(anatomical)
    image_file = nibabel.load(anatomical)
    affine = image_file.get_affine()

    header, streamlines = read_mrtrix_tracks(source, as_generator=True)
    trk_header = nibabel.trackvis.empty_header()
    trk_header['dim'] = [dx,dy,dz]
    trk_header['voxel_size'] = [vx,vy,vz]
    trk_header['n_count'] = header['count']

    axcode = nibabel.orientations.aff2axcodes(affine)
    trk_header['voxel_order'] = axcode[0]+axcode[1]+axcode[2]
    trk_header['vox_to_ras'] = affine
    transformed_streamlines = transform_to_affine(streamlines, trk_header, affine)
    trk_tracks = ((ii, None, None) for ii in transformed_streamlines)
    nibabel.trackvis.write(target, trk_tracks, trk_header)
    return target


def isAfreesurferStructure(directory):
    """Validate if the specified directory qualify as a freesurfer structure

    Args:
        directory: A directory that contain freesurfer structure

    Return:
        True if the specified directory if a freesurfer structure, False otherwise
    """
    def find(name):
        for root, dirs, files in os.walk(directory):
            if name in files:
                return True
        return False

    for image in ["T1.mgz", "aparc+aseg.mgz", "rh.ribbon.mgz", "lh.ribbon.mgz", "norm.mgz", "talairach.m3z"]:
        if not find(image):
            return False
    return True


def tckedit(source, roi, target, downsample= "2"):
    """ perform various editing operations on track files.

    Args:
        source: the input track file(s)
        roi:    specify an inclusion region of interest, as either a binary mask image, or as a sphere
                using 4 comma-separared values (x,y,z,radius)
        target: the output track file
        downsample: increase the density of points along the length of the streamline by some factor

    Returns:
        the output track file
    """
    cmd = "tckedit {} {} -downsample {} -quiet ".format(source, target, downsample)
    if isinstance(roi, basestring):
        cmd += " -include {}".format(roi)
    else:
        for element in roi:
            cmd += " -include {}".format(element)
    return util.launchCommand(cmd)


def computeDwiMaskFromFreesurfer(source, reference, sourceToResample, target, extraArgs):
    """

    Args:
        source:    an input image into the dwi space
        reference: usually the freesurfer normalize image
        sourceToResample: The image to apply the transform matrix: usually the freesurfer mask
        target: the output image name

        extraArgs: extra parameters to pass during the resampling computation step

    return
        A mask into the dwi native space

    """
    randomNumber = "{0:.6g}".format(random.randint(0,999999))

    #@TODO add dof as arguments parameters
    dummyTarget = "flirt_{}_target.nii.gz".format(randomNumber)
    matrix = "b0ToFressurfer_{}_transformation.mat".format(randomNumber)
    freesurferToB0 ='freesurferToB0_{}_transformation.mat'.format(randomNumber)

    cmd = "flirt -in {} -ref {} -omat {} -out {} {}".format(source, reference, matrix, dummyTarget, extraArgs)
    util.launchCommand(cmd)
    invertMatrix(matrix, freesurferToB0)
    cmd = "flirt -in {} -ref {} -applyxfm -init {} -out {} ".format(sourceToResample, source, freesurferToB0, target)
    util.launchCommand(cmd)
    return target


def computeNoiseMask(source, target):
    brainImage = nibabel.load(source)
    brainData = brainImage.get_data()
    brainData[brainData>0] = 1
    maskNoise = scipy.ndimage.morphology.binary_dilation(brainData, iterations=25)
    maskNoise[..., :maskNoise.shape[-1]//2] = 1
    maskNoise = ~maskNoise
    nibabel.save(nibabel.Nifti1Image(maskNoise.astype(numpy.uint8), brainImage.get_affine()), target)
    return target


def convertAndRestride(source, target, orientation):
    """Utility for converting between different file formats

    Args:
        source: The input source file
        target: The name of the resulting output file name

    """
    cmd = "mrconvert {} {} -stride {} -force -quiet"\
        .format(source, target, orientation)
    util.launchCommand(cmd)
    return target

def applyResampleFsl(source, reference, matrix, target, nearest = False):
    """Register an image with symmetric normalization and mutual information metric

    Args:
        source:
        reference: use this image as reference
        matrix:
        target: the output file name
        nearest: A boolean, process nearest neighbour interpolation

    Returns:
        return a file containing the resulting image transform
    """
    cmd = "flirt -in {} -ref {} -applyxfm -init {} -out {} ".format(source, reference, matrix, target)
    if nearest:
        cmd += "-interp nearestneighbour"
    util.launchCommand(cmd)
    return target


def applyRegistrationMrtrix(source , matrix, target):
    cmd = "mrtransform  {} -linear {} {} -quiet".format(source, matrix, target)
    util.launchCommand(cmd)
    return target


def setWorkingDirTractometry(workingDir, sourceBundles=None, sourceMetrics=None):
    """ Preparation for tractometry script from scilpy scil_run_tractometry
    :param workingDir: Current working Folder
    :param sourceDirBundles: Usually 17-tractquerier
    :param sourceDirMetrics:
    :return: Nothing
    """
    rawDir = 'raw'

    if os.path.exists(rawDir):
        rmtree(rawDir)

    os.mkdir(rawDir)

    bundlesDir = os.path.join(rawDir,'bundles')
    metricsDir = os.path.join(rawDir,'metrics')

    targetBundlesDir = os.path.join(workingDir, bundlesDir) + os.path.sep
    targetMetricsDir = os.path.join(workingDir, metricsDir) + os.path.sep

    if sourceBundles is not None:
        os.mkdir(bundlesDir)
        for bundle in sourceBundles:
            util.symlink(bundle, targetBundlesDir)

    if sourceMetrics is not None:
        os.mkdir(metricsDir)
        if type(sourceMetrics) is list:
            for metric in sourceMetrics:
                util.symlink(metric[0], targetMetricsDir, metric[1])


def runTractometry(config, source, target):
    cmd = "scil_run_tractometry.py --config_file {} {} {} -v -f ".format(config, source, target)
    util.launchCommand(cmd)
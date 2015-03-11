from lib.util import launchCommand
import util
import numpy
import nibabel
import os


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

    result = util.launchCommand(cmd)
    return result


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
    (stdout, stderr) = util.launchCommand(cmd)
    return stdout.splitlines()


def invertMatrix(source, target):
    """ invert a transformation matrices

    Args:
        source: an input transformation matrices
        target: an output transformation matrices name

    Returns:
        the resulting output transformation matrices name

    """
    cmd = "convert_xfm -inverse {} -omat {}".format(source, target)
    (stdout, stderr) = util.launchCommand(cmd)
    return target


def stride3DImage(source, target, layout="1,2,3" ):
    """perform a reorientation of the axes and flip the image into a different layout

    Args:
        source:           the input image
        layout:           comma-separated list that specify the strides.
        outputNamePrefix: a prefix to rename target filename

    Returns:
        the name of the resulting filename

    """
    cmd = "mrconvert {} {} -stride {}".format(source, target, layout)
    launchCommand(cmd)
    return target


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
        b_values = b_line[index].replace('\t',' ').split()
        gradient = numpy.matrix([[float(b_values[0]), float(b_values[1]),float(b_values[2])]])
        new_gradient = matrix*gradient.T

        values = str(float(new_gradient[0]))+'\t'+str(float(new_gradient[1]))+'\t'+str(float(new_gradient[2]))+'\t'+b_values[3].strip()+'\n'
        h.write(values)

    h.close()
    return target


def bValsBVecs2BEnc(bvecsFilename, bvalsFilename, target):
    """Create a B encoding gradient file base on bVals and bVecs encoding file

    Args:
        bvecsFilename: a vector value file.
        bvalsFilename: a gradient b value encoding file.

    Returns:
        the resulting b encoding file

    """
    b = open(bvalsFilename,"r")
    v = open(bvecsFilename,"r")
    bVals = b.readlines()
    bVecsLines = v.readlines()
    b.close()
    v.close()
    bVecs = []
    for bvecs in bVecsLines:
        bVecs.append(bvecs.strip().split())

    f = open(target,'w')
    for index, bVal in enumerate(bVals.pop().strip().split()):
        f.write("{}\t{}\t{}\t{}\n".format(bVecs[0][index], bVecs[1][index], bVecs[2][index], bVal))
    f.close()
    return target


def bEnc2BVecs(source, target):
    """Create a gradient vector file base on B encoging file

    Args:
        source: a b gradient encoding file.

    Returns:
        the resulting b vector encoding file

    """
    bvecs = []
    with open(source, 'r') as f:
        for line in f.readlines():
            tokens = line.split()
            if len(tokens)==4:
                bvecs.append(tokens[0:3])
    bvecs = zip(*bvecs)

    v = open(target,"w")
    for items in bvecs:
        for item in items:
            v.write("{} ".format(item))
        v.write("\n")
    v.close()

    return target


def bEnc2BVals(source, target):
    """Create a gradient b value file base on B encoging file

    Args:
        source: a b gradient encoding file.

    Returns:
        the resulting b value encoding file

    """
    bVals = []
    with open(source, 'r') as f:
        for line in f.readlines():
            tokens = line.split()
            bVals.append(tokens.pop(3))

    b = open(target,"w")
    for bval in bVals:
        b.write("{} ".format(bval))
    b.close()

    return target


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
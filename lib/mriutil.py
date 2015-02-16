from lib.util import launchCommand
import util
import numpy
import nipy
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
    print 'cmd=',cmd
    result = util.launchCommand(cmd)
    #Spm do not support .gz format, so uncompress nifty file
    print "result =", result
    #util.gunzip("{}.gz".format(target))
    return result


def extractFirstB0FromDwi(source, target, bval, nthreads = "1"):
    """Perform an extraction of the first b0 image found into a DWI image

    Args:
        source: The input image
        target: The resulting output name
        bval:   A gradient encoding B0 values file name

    Returns:
         A tuple of 3 elements representing (the command launch, the stdout and stderr of the execution)
    """
    return extractSubVolume(source, target, "3", getFirstB0IndexFromDwi(bval), nthreads)


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
    cmd = "convert_xfm -inverse {} -omat {}".format(source, target)
    (stdout, stderr) = util.launchCommand(cmd)
    return target


def strideImage(source, layout, target):


    if len(getMriDimensions(source)) == 3:
        cmd = "mrconvert {} {} -stride {}"
    else:
        cmd = "mrconvert {} {} -stride {},4"
    print cmd.format(source, target, layout)
    launchCommand(cmd.format(source, target, layout))
    return target


def getMrinfoFieldValues(text, field, delimiter=""):
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
    return getMrinfoFieldValues(mrinfo(source), "Dimensions:", "x")


def getMriVoxelSize(source):
    return getMrinfoFieldValues(mrinfo(source), "Voxel size:", "x")


def getNbDirectionsFromDWI(source):
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
    return ",".join(getMrinfoFieldValues(mrinfo(source), "Data strides:").strip("[]").split())


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


def getFirstB0IndexFromDwi(bval):
    """Return the index of the first B0 value found into B0 Value encoding file.

    Args:
        bval:  A B value encoging file

    Returns:
        The index of the first b0 found in the file

    """
    for line in open(bval,'r').readlines():
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


def bValBVec2BEnc(bvalFilename, bvecFilename, target):
    """Create a B encoding gradient file base on Bval and Bvec encoding file

    Args:
        bvalFilename: a gradient b value encoding file.
        bvalFilename: a vector value file.

    Returns:
        the resulting b encoding file

    """
    b = open(bvalFilename,"r")
    v = open(bvecFilename,"r")
    bvals = b.readlines()
    bVecsLines = v.readlines()
    b.close()
    v.close()

    bVecs = []
    for bVec in bVecsLines:
        bVecs.append(bVec.strip().split())

    f = open(target,'w')
    for index, bval in enumerate(bvals.pop().strip().split()):
        f.write("{}\t{}\t{}\t{}\n".format(bVecs[0][index], bVecs[1][index], bVecs[2][index],bval))
    f.close()
    return target


def bEnc2BVec(source, target):
    """Create a gradient vector file base on B encoging file

    Args:
        source: a b gradient encoding file.

    Returns:
        the resulting b vector encoding file

    """
    bvecs = []

    f = open(source, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
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


def bEnc2BVal(source, target):
    """Create a gradient b value file base on B encoging file

    Args:
        source: a b gradient encoding file.

    Returns:
        the resulting b value encoding file

    """
    bvals = []

    f = open(source,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        tokens = line.split()
        bvals.append(tokens.pop(3))

    b = open(target,"w")

    for bval in bvals:
        b.write("{} ".format(bval))
    b.close()

    return target

def strideEncodingFile(source, originalStrides, expectedStrides, target):
    """
        Change strides from an encoding file to a new layout
    Args:
        source: An Vector encoding file with .b or .bvec  extension
        originalStrides: a 3 values comma separated string representing the initial layout into the dwi image
        expectedStrides: a 3 values comma separated string representing the layout of the target file
        target: the output filename

    Return:
        the output filename

    """

    def __changeSignBEnc(lines):
        """Closures function that changes signs of the gradient encoding vector in respect of the expected layout
           originalLayout and expectedLayout are inherit from strideEncodingFile environment

        Args:
            lines: A 4 columns gradient orientation array

        Returns:
            A 4 columns gradient orientation array

        """
        results = []
        signChanges = __isSignChange(originalLayout, expectedLayout)
        for line in lines:
            tokens = line.split()
            for i in [0, 1, 2]:
                if signChanges[i]:
                    if tokens[i][0] == "-":
                        tokens[i] = tokens[i].replace("-",'')
                    else:
                        tokens[i] = "-{}".format(tokens[i])
            results.append(tokens)
        return results

    #this function is apply before the list is permute
    def __changeSignBVec(lines):
        """Closures function that changes signs of the gradient encoding vector in respect of the expected layout
           originalLayout and expectedLayout are inherit from strideEncodingFile environment

        Args:
            lines: A 3 rows gradient orientation array

        Returns:
            A 3 rows gradient orientation array

        """
        results = []
        signChanges = __isSignChange(originalLayout, expectedLayout)
        for i in [0, 1, 2]:
            vector = []
            for element in lines[i].split():
                if signChanges[i]:
                    if element[0] == "-":
                        element = element.replace("-", '')
                    else:
                        element = "-{}".format(element)
                vector.append(element)
            results.append(vector)
        return results

    def __findSignOfElementInList(element, list):
        """Closures function that return the sign (positive or negative) of the element into a list that have the same value
         as the element given as entry
        Args:
            element: The value of the element to find into the list
            list: A list of string elements that represent positive or negative integer

        Returns:
            the sign "+" if the element in the list is greater or equal to zero, "-" otherwise

        """
        for item in list:
            if element.replace("-","") in item:
                if "-" in item:
                    return "-"
                else:
                    return "+"
        return False


    def __isSignChange():
        """Closures function that return if a sign change is request for each stride (direction)
           originalLayout and expectedLayout are inherit from strideEncodingFile environment

        Args:
            originalLayout: A 3 elements list representing the actual stride of the dwi image
            expectedLayout: A 3 elements list representing the expected final layout
        Returns:
            A 3 Booleans array that indicate if a sign change need to be apply at each position

        """
        signs = [False, False, False]
        for index in [0,1,2]:
            if __findSignOfElementInList(originalLayout[index], originalLayout) \
                    !=__findSignOfElementInList(originalLayout[index], expectedLayout):
                signs[index] = True
        return signs


    def __permuteColumnBEnc(lines):
        """Closures function that permute column from original layout to  the expect layout
           originalLayout and expectedLayout are inherit from strideEncodingFile environment

        Args:
            lines: a b encoding (4 columns) list of elements

        Returns:
            a list of elements permute
        """
        results = []
        for line in lines:
            tmp = [line[originalIndexes['1']], line[originalIndexes['2']], line[originalIndexes['3']], line[3]]
            results.append([tmp[expectedIndexes['1']], tmp[expectedIndexes['2']],tmp[expectedIndexes['3']], line[3]])
        return results


    def __permuteColumnBVec(lines):
        """Closures function that permute column from original layout to  the expect layout
           originalLayout and expectedLayout are inherit from strideEncodingFile environment

        Args:
            lines: a b vector encoding (3 rows) list of elements

        Returns:
            a list of elements permute
        """
        tmp = [lines[originalIndexes['1']], lines[originalIndexes['2']],lines[originalIndexes['3']]]
        return [tmp[expectedIndexes['1']], tmp[expectedIndexes['2']],tmp[expectedIndexes['3']]]

    originalLayout = originalStrides.split(",")
    expectedLayout = expectedStrides.split(",")

    originalIndexes = {originalLayout[0].replace('-', ''):0,
                       originalLayout[1].replace('-', ''):1,
                       originalLayout[2].replace('-', ''):2}

    expectedIndexes = {expectedLayout[0].replace('-', ''):0,
                       expectedLayout[1].replace('-', ''):1,
                       expectedLayout[2].replace('-', ''):2}


    f = open(source,'r')
    lines = f.readlines()
    f.close()

    b = open(target, "w")
    if len(lines[0].split()) == 4:
        lines = __changeSignBEnc(lines)
        lines = __permuteColumnBEnc(lines)
        for line in lines:
                b.write("{}\t{}\t{}\t{}\n".format(line[0], line[1], line[2], line[3]))

    elif len(lines) == 3:
        lines = __changeSignBVec(lines)
        lines = __permuteColumnBVec(lines)
        for items in lines:
            for item in items:
                b.write("{} ".format(item))
            b.write("\n")

    b.close()
    return target


def extractFreesurferStructure(values, source, target):
    """ Extract given value from an image

    Args:
        values: A list of values to extract from an input image
        source: An mri image

    returns:
        a new image that contain areas specified by values
    """
    image = nipy.io.api.load_image(source)
    array = numpy.array(image._data)
    c = []
    for value in values:
        c.append(numpy.where(array==value))
    array.fill(0)
    for i in range(len(values)):
        array[c[i]] = 1
    image._data = array
    
    if not os.path.exists(target):
        nipy.io.api.save_image(image, target)
    return target

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


def strideImage(source, target):
    if len(getMriDimensions(source)) == 3:
        cmd = "mrconvert {} {} -stride 1,2,3"
    else:
        cmd = "mrconvert {} {} -stride 1,2,3,4"
    launchCommand(cmd.format(source, target))
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
    """ return datas stride layout

    Args:
        source: A mri image

    Returns:
        An array of string elements representing the layout of the image

    """
    return getMrinfoFieldValues(mrinfo(source), "Data strides:").strip("[]").split()


def isDataStridesOrientationExpected(source):
    strides = getDataStridesOrientation(source)
    if len(strides) >= 3:
        if strides[0].strip() in "1" and strides[1].strip() in "2" and strides[2].strip() in "3":
            return True
    return False


def getFirstB0IndexFromDwi(bval):
    for line in open(bval,'r').readlines():
            b0s = line.strip().split()
            return b0s.index('0')
    return False


def applyGradientCorrection(bFilename, eddyFilename, target):

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


def strideEncodingFile(source, originalLayout, target):
    """
        Change strides from an encoding file to  layout 1,2,3
    Args:
        source: An Vector encoding file with .b or .bvec  extension
        originalLayout: the initial layout of the dwi image
        target: the output filename

    Return:
        the output filename

    """

    def changeSignBEnc(lines):
        results = []
        for line in lines:
            tokens = line.split()
            for i in [0, 1, 2]:
                if int(originalLayout[i]) < 0:
                    if tokens[i][0] == "-":
                        tokens[i] = tokens[i].replace("-",'')
                    else:
                        tokens[i] = "-{}".format(tokens[i])
            results.append(tokens)
        return results

    def changeSignBVec(lines):
        results = []
        for i in [0, 1, 2]:
            vector = []
            for element in lines[i].split():
                if int(originalLayout[i]) < 0:
                    if element[0] == "-":
                        element = element.replace("-", '')
                    else:
                        element = "-{}".format(element)
                vector.append(element)
            results.append(vector)
        return results

    def permuteColumnBEnc(lines):
        results = []
        for line in lines:
            results.append([line[indexes['1']],line[indexes['2']],line[indexes['3']],line[3]])
        return results


    def permuteColumnBVec(lines):
        return [lines[indexes['1']], lines[indexes['2']],lines[indexes['3']]]

    indexes = {originalLayout[0].replace('-',''): 0,
               originalLayout[1].replace('-',''): 1,
               originalLayout[2].replace('-',''): 2}

    f = open(source,'r')
    lines = f.readlines()
    f.close()

    b = open(target, "w")
    if len(lines[0].split()) == 4:
        lines = changeSignBEnc(lines)
        lines = permuteColumnBEnc(lines)
        for line in lines:
                b.write("{}\t{}\t{}\t{}\n".format(line[0], line[1], line[2], line[3]))

    elif len(lines) == 3:
        print "orig =",lines
        lines = changeSignBVec(lines)
        lines = permuteColumnBVec(lines)
        print "finish =",lines
        for items in lines:
            for item in items:
                b.write("{} ".format(item))
            b.write("\n")

    b.close()
    return target

def extractFreesurferStructure(l, source, target):
    a = nipy.io.api.load_image(source)
    b = numpy.array(a._data)
    c = []
    for i in l:
        c.append(numpy.where(b==i))
    b.fill(0)
    for i in range(len(l)):
        b[c[i]] = 1
    a._data = b
    
    if not os.path.exists(target):
        nipy.io.api.save_image(a, target)
    return target

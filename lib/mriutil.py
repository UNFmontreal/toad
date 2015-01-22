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

    result = util.launchCommand(cmd)
    #Spm do not support .gz format, so uncompress nifty file
    util.gunzip("{}.gz".format(target))
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


def validateDataStrides(source):
    strides = getMrinfoFieldValues(mrinfo(source), "Data strides:")
    tokens = strides.strip("[]").split()
    if len(tokens) >= 3:
        if tokens[0].strip() in "1" and tokens[1].strip() in "2" and tokens[2].strip() in "3": 
            return True
    return False


def getFirstB0IndexFromDwi(bval):
    for line in open(bval,'r').readlines():
            b0s = line.strip().split()
            return b0s.index('0')
    return False


def applyGradientCorrection(bFilename, eddyFilename, target):

    output = os.path.join(target, os.path.basename(bFilename).replace(".b","_eddy.b"))

    f = open(eddyFilename, 'r')
    g = open(bFilename, 'r')
    eddys = f.readlines()
    b_line = g.readlines()
    f.close()
    g.close()

    h = open(output, 'w')

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
    return output


def bValBVec2BEnc(bvalFilename, bvecFilename, outputDir):
    bEncodingFilename = os.path.join(outputDir, os.path.basename(bvalFilename).replace(".bval",".b"))

    b = open(bvalFilename,"r")
    v = open(bvecFilename,"r")
    bvals = b.readlines()
    bVecsLines = v.readlines()
    b.close()
    v.close()

    bVecs = []
    for bVec in bVecsLines:
        bVecs.append(bVec.strip().split())

    f = open(bEncodingFilename,'w')
    for index, bval in enumerate(bvals.pop().strip().split()):
        f.write("{}\t{}\t{}\t{}\n".format(bVecs[0][index], bVecs[1][index], bVecs[2][index],bval, ))
    f.close()
    return bEncodingFilename


def bEnc2BVec(source, outputDir):
    bvecFilename = os.path.join(outputDir, os.path.basename(source).replace(".b",".bvec"))
    bvecs = []

    f = open(source, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        tokens = line.split()
        if len(tokens)==4:
            bvecs.append(tokens[0:3])
    bvecs = zip(*bvecs)

    v = open(bvecFilename,"w")

    for items in bvecs:
        for item in items:
            v.write("{} ".format(item))
        v.write("\n")
    v.close()

    return bvecFilename


def bEnc2BVal(source, outputDir):

    bvalFilename = os.path.join(outputDir,os.path.basename(source).replace(".b",".bval"))
    bvals = []

    f = open(source,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        tokens = line.split()
        bvals.append(tokens.pop(3))

    b = open(bvalFilename,"w")

    for bval in bvals:
        b.write("{} ".format(bval))
    b.close()

    return bvalFilename


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

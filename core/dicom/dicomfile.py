import struct

from dicom.filereader import read_file
from dicom.tag import Tag
from dicom.errors import InvalidDicomError

from ascconv import Ascconv
from lib import util

manufacturers = ['Philips', 'GE', 'SIEMENS']  # Different manufacturers

class DicomFile(Ascconv):

    def __init__(self, filename):
        self.__filename = filename
        self.__isDicom = False
        self.__manufacturer = None
        self.__patientName = None
        self.__seriesDescription = None
        self.__seriesNumber = None
        self.__instanceNumber = None
        self.__SequenceName = None
        self.__channel = None

        self.__bandwidthPerPixelPhaseEncode = None
        self.__echoSpacing = None
        self.__tr = None  # Repetition time
        self.__te = None  # Echo time
        self.__ti = None  # Time Inversion
        self.__flipAngle = None  # FlipAngle
        self.__numSlices = None  # Num of slices
        self.__fov = None  # FOV: Field Of View
        self.__matrixSize = None  # Matrix size
        self.__voxelSize = None  # Voxel size

        self.__initialized()

    def __repr__(self):
        return "filename = {}, manufacturer ={}, patientName={}, seriesDescription={}, seriesNumber={}," \
               " instanceNumber={}, echoTime={}, channel={}, isDicom = {}"\
                .format(self.__filename, self.__manufacturer, self.__patientName,
                        self.__seriesDescription, self.__seriesNumber, self.__instanceNumber,
                        self.__te, self.__channel, self.__isDicom)

    def __initialized(self):

        try:
            header = read_file(self.__filename, defer_size=None, stop_before_pixels=True)

        except InvalidDicomError:
            self.__isDicom = False
            return
        try:

            #find the manufacturer
            self.__manufacturer = 'UNKNOWN'
            if 'Manufacturer' in header:
                for manufacturer in manufacturers:
                    if manufacturer in header.Manufacturer:
                        self.__manufacturer = manufacturer

            self.__patientName = util.slugify(header.PatientName)
            self.__seriesDescription = util.slugify(header.SeriesDescription)
            self.__seriesNumber = header.SeriesNumber
            self.__instanceNumber = header.InstanceNumber

            self.__tr = float(header.RepetitionTime)  # TR Repetition Time
            self.__te = float(header.EchoTime)  # TE Echo Time
            self.__flipAngle = float(header.FlipAngle)  # Flip Angle

            self.__matrixSize = [value for value in header.AcquisitionMatrix if value != 0]  # Matrix Size
            self.__voxelSize = map(int, header.PixelSpacing)  # Voxel size
            self.__fov = self.__matrixSize[0] * self.__voxelSize[0]  # Compute FOV

            self.__isDicom = True

        except AttributeError as a:
            if "EchoTime" in a.message:
                try:
                    self.__te = header[Tag((0x2001, 0x1025))].value
                    self.__isDicom = True
                except KeyError as k:
                    self.__isDicom = False
            else:
                 self.__isDicom = False

        if self.isSiemens():

            if 'DIFFUSION' and 'MOSAIC' in header.ImageType:  # If Diffusion Acquistion
                self.__SequenceName = 'Diffusion'
            elif 'DIFFUSION' in header.ImageType:  # If b0 Acquistion
                self.__SequenceName = 'b0'
            elif 'M' and 'NORM' in header.ImageType:  # If T1 Acquisition
                self.__SequenceName = 'Structural T1'
                self.__ti = float(header.InversionTime)
            elif 'P' in header.ImageType:  # If Phase acquisition
                self.__SequenceName = 'Phase'
            else:  #  If Magnitude acquisition
                self.__SequenceName = 'Magnitude'

            #inherith Siemens ascconv properties
            Ascconv.__init__(self, self.__filename)
            bandwidthPerPixelPhaseEncodeTag = Tag((0x0019, 0x1028))

            try:
                if header.has_key(bandwidthPerPixelPhaseEncodeTag):
                    val = header[bandwidthPerPixelPhaseEncodeTag].value
                    try:
                        self.__bandwidthPerPixelPhaseEncode = float(val)
                    except ValueError:
                        # some data have wrong VR in dicom, try to unpack
                        self.__bandwidthPerPixelPhaseEncode = struct.unpack('d', val)[0]

                self.__echoSpacing = 1/(self.__bandwidthPerPixelPhaseEncode* self.getEpiFactor()) *1000.0 * \
                              self.getPatFactor() * self.getPhaseResolution() * \
                              self.getPhaseOversampling()

            except (KeyError, IndexError, TypeError, ValueError):
                self.__echoSpacing = None


    def getFileName(self):
        return self.__filename

    def getAcquisitionName(self):
        return "{:02d}-{}".format(int(self.__seriesNumber), self.__seriesDescription)

    def getSessionName(self):
        return self.__patientName

    def getSeriesDescription(self):
        return self.__seriesDescription

    def getSeriesNumber(self):
        return self.__seriesNumber

    def getInstanceNumber(self):
        return self.__instanceNumber

    def getEchoTime(self):
        return self.__te

    def getEchoSpacing(self):
        return self.__echoSpacing

    def getRepetitionTime(self):
        return self.__tr

    def getInversionTime(self):
        return self.__ti

    def getSequenceName(self):
        return self.__SequenceName

    def getFlipAngle(self):
        return self.__flipAngle

    def getFOV(self):
        return self.__fov

    def getVoxelSize(self):
        return self.__voxelSize

    def getMatrixSize(self):
        return self.__matrixSize

    def getNumDirections(self):
        return self.__numDirections

    def isDicom(self):
        return self.__isDicom

    def isSiemens(self):
        return self.__manufacturer == 'SIEMENS'

# -*- coding: utf-8 -*-
import math

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]

class Ascconv(object):

    def __init__(self, filename):
        self.__fileName = filename
        self.__ascconvFound = False

        # If the phase encoding direction is AP won't find anything to set __phaseEncodingDirection
        # otherwise it will be set correctly
        self.__phaseEncodingDirection = 1

        self.__numSlices = None # Always available
        self.__patFactor = None  # Always available PAT Factor
        self.__epiFactor = None  # Always available Epi Factor
        self.__phaseResolution = None  # 1
        self.__phaseOversampling = 1  # otherwise 1 + __phaseOversampling
        self.__numberArrayCoil = 0  # 0
        self.__numDirections = None
        self.__bValue = None
        self.__initialize()


    def __repr__(self):
        return "filename={}, phaseEncodingDirection={}, patFactor={}, epiFactor={}, " \
               "phaseResolution={}, phaseOversampling ={}" \
                    .format(self.__fileName,
                            self.__phaseEncodingDirection,
                            self.__patFactor,
                            self.__epiFactor,
                            self.__phaseResolution,
                            self.__phaseOversampling)

    def isValid(self):
        return self.__ascconvFound

    def getFileName(self):
        return self.__fileName

    def getPhaseEncodingDirection(self):
        return self.__phaseEncodingDirection

    def getPatFactor(self):
        return self.__patFactor

    def getEpiFactor(self):
        return self.__epiFactor

    def getPhaseResolution(self):
        return self.__phaseResolution

    def getPhaseOversampling(self):
        return  self.__phaseOversampling

    def getNumberArrayCoil(self):
        return self.__numberArrayCoil

    def getbValue(self):
        return self.__bValue

    def getNumberDirections(self):
        return self.__numDirections

    def getNumberSlices(self):
        return self.__numSlices

    def __initialize(self):
        with open(self.__fileName, 'r') as f:
            ascconv = []
            for line in f.readlines():
                if "### ASCCONV BEGIN " in line:
                    self.__ascconvFound = True
                if "### ASCCONV END " in line:
                    break
                if self.__ascconvFound:
                    ascconv.append(line)

            for line in ascconv:
                line = line.lower()

                if "coil" in line and "meas" in line and "lrxchannelconnected" in line:
                    self.__numberArrayCoil += 1

                elif "sslicearray.asslice" in line and ".dinplanerot" in line:
                    self.__phaseEncodingDirection = int(self.__returnPhaseEncodingDirection(line))

                elif "spat.laccelfactpe" in line:
                    try:
                        self.__patFactor = float(line.split("=")[-1].strip())
                    except ValueError:
                        pass
                elif "skspace.lphaseencodinglines" in line:
                    try:
                        self.__epiFactor = float(line.split("=")[-1].strip())
                    except ValueError:
                        pass
                elif "skspace.dphaseresolution" in line:
                    try:
                        self.__phaseResolution= float(line.split("=")[-1].strip())
                    except ValueError:
                        pass

                elif "skspace.dphaseoversamplingfordialog" in line:
                    try:
                        # 1 + phase oversampling (ex: 1 + 0.25)
                        self.__phaseOversampling = 1 + float(line.split("=")[-1].strip())
                    except ValueError:
                        pass

                elif "sdiffusion.albvalue[1]" in line:
                    try:
                        self.__bValue = int(line.split("=")[-1].strip())
                    except ValueError:
                        pass

                elif "diffusion.ldiffdirections" in line:
                    try:
                        self.__numDirections = int(line.split("=")[-1].strip())
                    except ValueError:
                        pass

                elif "skspace.limagesperslab" in line:
                    try:
                        self.__numSlices = int(line.split("=")[-1].strip())
                    except ValueError:
                        pass


    def __returnPhaseEncodingDirection(self, line):

        tolerance = 0.2
        try:
            value = float(line.split("=")[-1].strip())
        except ValueError:
            return 1

        if value < tolerance and value > -tolerance:
           return 1  #between -0.2 and 0.2  A>>P

        if (value > math.pi - tolerance) or (value < tolerance - math.pi):
            return 0  #greater than  2.94  or smaller than -2.94  #P>>A

        if (value > (math.pi/2) - tolerance) and (value < (math.pi/2)+tolerance):
            return 2  #R>>L

        if (value < math.copysign((math.pi/2)-tolerance,-0.0)) and (value > math.copysign((math.pi/2)+tolerance, -0.0)):
             return 3  #L>>R

        return 1

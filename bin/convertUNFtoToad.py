#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import sys
import os


__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright 2014, The Toad Project"
__credits__ = ["Mathieu Desrosiers"]
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Mathieu Desrosiers"
__email__ = "mathieu.desrosiers@criugm.qc.ca"
__status__ = "Development"



#@des gens pourrait avoir plusieurs dti dans leur packqage

-magnituges .. ,
-Est-ce que l'on peut produire la phase avant la magnitude'?
-l'autre carte est constitué de la phase est ...'



sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from lib import util

__author__ = 'mathieu'


junks = ["aascout", "localizer", "tensor", "gre_field_map",'mprage_12ch_ipat3']
anatLabels = ["mprage"]
dwiLabels = ["dti_", "dwi_", "ep2d_diff_mddw_64_p2"]
flairLabels = ["flair"]
swiLabels = ["swi"]



if len(sys.argv) < 2:
        rootDir = "."
else:
        rootDir = sys.argv[1]

rootDir = os.path.abspath(rootDir)
resultDir = os.path.join(rootDir, os.path.basename(rootDir))
if not os.path.exists(resultDir):
    os.mkdir(resultDir)


def removeKey(d, key):
    r = dict(d)
    del r[key]
    return r

#find Magnitude field map image image if exists
diffOfEchoes = 0
#sequences =

#sort field map
fieldMaps = {"magnitudes": None , "magnitudesDWI": None , "phases": None , "phasesDWI": None}
for sequence in  glob.glob("{}/??-*gre_field_map*".format(rootDir)):
    dirPaths = glob.glob("{}/echo_*".format(sequence))
    if len(dirPaths) == 2:
        if "_dti" in sequence.lower() or "_dwi" in sequence.lower():
            if fieldMaps["magnitudesDWI"]:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(fieldMaps["magnitudesDWI"]).split("-")[0])
                if current > dictValue:
                    fieldMaps["magnitudesDWI"] = sequence

            else:
                fieldMaps["magnitudesDWI"] = sequence
        else:
            if fieldMaps["magnitudes"]:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(fieldMaps["magnitudes"]).split("-")[0])
                if current > dictValue:
                    fieldMaps["magnitudes"] = sequence

            else:
                fieldMaps["magnitudes"] = sequence

    elif len(dirPaths) == 1:
        if "_dti" in sequence.lower() or "_dwi" in sequence.lower():
            if fieldMaps["phasesDWI"]:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(fieldMaps["phasesDWI"]).split("-")[0])
                if current > dictValue:
                    fieldMaps["phasesDWI"] = sequence
            else:
                fieldMaps["phasesDWI"] = sequence
        else:
            if fieldMaps["phases"]:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(fieldMaps["phases"]).split("-")[0])
                if current > dictValue:
                    fieldMaps["phases"] = sequence
            else:
                fieldMaps["phases"] = sequence



#compute dwellTime between magnitude images
magnitudesDWIEchoes = glob.glob("{}/echo_*".format(fieldMaps["magnitudesDWI"]))
value1 = float(os.path.basename(magnitudesDWIEchoes[0]).strip("echo_"))
value2 = float(os.path.basename(magnitudesDWIEchoes[1]).strip("echo_"))
fieldMaps["dwellTimeDWI"] = str(value2 - value1)

magnitudesEchoes = glob.glob("{}/echo_*".format(fieldMaps["magnitudesDWI"]))
value1 = float(os.path.basename(magnitudesEchoes[0]).strip("echo_"))
value2 = float(os.path.basename(magnitudesEchoes[1]).strip("echo_"))
fieldMaps["dwellTime"] = str(value2 - value1)


paths = glob.glob("{}/??-*".format(rootDir))
sequences = {}
for path in paths:
    sequences[os.path.basename(path).split("-")[1].lower()] = path

#remove junk
for key, value in sequences.iteritems():
    for junk in junks:
        if junk in key:
            sequences = removeKey(sequences, key)

print sequences


#filter for anatomical sequence
anatValue = {"anat": []}
for key, value in sequences.iteritems():
    for anat in anatLabels:
        if anat in key:
            if anatValue["anat"] is not None:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(anatValue["anat"]).split("-")[0])
            else:
                anatValue["anat"] = value

print anatValue


#filter for flair sequence
flairValue = {"flair": None}
for key, value in sequences.iteritems():
    for flair in flairLabels:
        if anat in key:
            if anatValue["anat"] is not None:
                current = int(os.path.basename(sequence).split("-")[0])
                dictValue = int(os.path.basename(anatValue["anat"]).split("-")[0])
            else:
                anatValue["anat"] = value

print anatValue


flairLabels = ["flair"]
swiLabels = ["swi"]


"""
for sequence in sequences:
    dirPaths = glob.glob("{}/echo_*".format(sequence))
    if len(dirPaths) == 2:
        try:
            value1 = float(os.path.basename(dirPaths[0]).strip("echo_"))
            value2 = float(os.path.basename(dirPaths[1]).strip("echo_"))
            diffOfEchoes = value2 - value1

            cmd = "mrconvert {} {}/magnitude.nii".format(dirPaths[1], resultDir)
            print cmd
            sys.exit()
            #util.launchCommand(cmd)

        except ValueError:
            pass

    elif len(dirPaths) == 1:
        cmd = "mrconvert {} {}/phase.nii".format(dirPaths[0], resultDir)
        print cmd
        util.launchCommand(cmd)

#creates gradients directions encoding file
sequences = glob.glob("{}/??-*".format(rootDir))
for sequence in sequences:
    if os.path.isdir(sequence):
        [subpath, path] = os.path.split(sequence)
        filename = path.split("-")[1]
        cmd = "mrconvert {} {}/{}.nii".format(sequence, resultDir, filename)
        util.launchCommand(cmd)

        cmd = "mrinfo {} -export_grad_mrtrix {}/{}.b".format(sequence, resultDir, filename)
        print cmd
        util.launchCommand(cmd)






#cleanup junk sequences
for image in glob.glob("{}/*.nii".format(resultDir)):
    for junk in junks:
        if junk in os.path.basename(image):
                os.remove(image)


for (dirpath, dirnames, filenames) in os.walk(rootDir):
    if glob.glob("{}/*.dcm".format(dirpath)):
        dirpath = os.path.abspath(dirpath)
        [path, filename] = os.path.split(dirpath)
        print path
        print filename
        if "echo_" in filename:
            echoTime = filename
            [path, filename] = os.path.split(path)

            filename+=echoTime.strip('echo')

            sys.exit()
        cmd = "mrconvert {} {}.nii".format(dirpath, filename.split('-')[1])
        print cmd


#convert all images
for (dirpath, dirnames, filenames) in os.walk(rootDir):
    if glob.glob("{}/*.dcm".format(dirpath)):

        dirpath = os.path.abspath(dirpath)
        [path, filename] = os.path.split(dirpath)
        if "echo_" in filename:
            echoTime = filename
            [path, filename] = os.path.split(path)
            filename+=echoTime.strip('echo')
        cmd = "mrconvert {} {}.nii".format(dirpath, filename.split('-')[1])
        print cmd


#remove all co images
for (dirpath, dirnames, filenames) in os.walk(rootDir):
    coImages = glob.glob("{}/co*.nii".format(dirpath))
    if coImages:
        for coImage in coImages:
        cmd = "rm {}".format(coImage)
        #util.launchCommand(cmd)
        print cmd

#rename all images
for (dirpath, dirnames, images) in os.walk(rootDir):
        #oImages = glob.glob("{}/o*.nii".format(dirpath))
        images = glob.glob("{}/*.nii".format(dirpath))
        bvecs = glob.glob("{}/*.bvec".format(dirpath))
        bvals = glob.glob("{}/*.bval".format(dirpath))

        #if oImages:
        #        for image in oImages:
        #                [dir, filename] = os.path.split(image)
        #                newImageName = dir.split("-")[1]
        #                cmd = "mv {} {}.nii".format(image, newImageName)
        #                print cmd
        if images:
                for image in images:
                        [dir, filename] = os.path.split(image)
                        newImageName = dir.split("-")[1]
                        cmd = "mv {} {}.nii".format(image, newImageName)
                        print cmd

        if bvecs:
                for bvec in bvecs:
                        [dir, filename] = os.path.split(bvec)
                        newImageName = dir.split("-")[1]
                        cmd = "mv {} {}.bvec".format(bvec, newImageName)
                        print cmd

        if bvals:
                for bval in bvals:
                        [dir, filename] = os.path.split(image)
                        newImageName = dir.split("-")[1]
                        cmd = "mv {} {}.bval".format(bval, newImageName)
                        print cmd

#move images



#create config.cfg
"""
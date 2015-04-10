#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import argparse
import glob
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from lib import util

__author__ = "Guillaume Vallet, Mathieu Desrosiers"
__copyright__ = "Copyright 2015, The Toad Project"
__credits__ = ["Guillaume Vallet", "Mathieu Desrosiers"]
__license__ = "GPL"
__version__ = "0.0"
__maintainer__ = "Mathieu Desrosiers"
__email__ = "mathieu.desrosiers@criugm.qc.ca"
__status__ = "Development"

def __parseArguments():
    """Prepare and parse user friendly command line arguments for sys.argv.


    Returns:
        a args stucture containing command lines arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description ="""\n

         """)
    parser.add_argument("inputFolder", help="A UNF mri session")
    parser.add_argument("subjectName",  nargs='?', help="Specify a name to add after the prefix")
    parser.add_argument("-c", "--config", nargs='?',metavar=('filename'), required=False,
                            help="Specify the location of an alternative the config.cfg as input. Defaults: etc/config.cfg")
    parser.add_argument("-n","--noConfig", help="Do not produce the config.cfg file into the root folder", action="store_true")
    args = parser.parse_args()
    return args

def __parsePrefixFromConfig(arguments):

    items = {}
    config = ConfigParser.ConfigParser()
    configFiles = []
    configFiles.append(os.path.dirname(os.path.realpath(__file__)).replace("bin", "etc/config.cfg"))
    if arguments.config:
        if os.path.isfile(arguments.config):
            configFiles.append(arguments.config)

    for configFile in configFiles:
        config.read(configFile)

    for item in config.items("prefix"):
        items[item[0]] = item[1]
    return items

def __exists(structure, element):
    for index, value in structure:
        if index == element:
            return True
    return False

def __listMriDirectories(source):

    structure = []
    dicoms = glob.glob("{}/*/*.dcm".format(source))
    dicoms.extend( glob.glob("{}/*/*/*.dcm".format(source)))
    for dicom in dicoms:
        fullpath = os.path.split(dicom)[0]
        directory = fullpath.replace(source, '')

        if directory[0] == "/":
            directory = directory[1:]

        if not __exists(structure, directory):
            structure.append((directory, fullpath))
    return structure


def __getName(question):
    prefix = raw_input("Please enter the prefix of the" + question + " files:")
    return prefix


def __chooseFolder(folders, question):
    structure = []

    for index, value in enumerate(folders):
        structure.append((index+1, value))

    while True:
        print("\n\n"+45*"-")
        print("Please select the folder in which to find the " + question + " files:\n")
        print(" 0.  Files are not in folders")
        for index, value in structure:
            print("{:2d}.  {}".format(index, value[0]))
        print("99.  None\n")

        #some validation
        choice = raw_input("Enter your choice [0-"+str(len(folders))+"] or select none [99]:")
        if int(choice) == 0 or 0 <= int(choice)-1 <= len(folders):
           break

        elif int(choice) == 99:
            return

        else:
            print("Invalid choice, please enter a valid number")

    try:
        for index, value in structure:
            if index == int(choice):
                return(value)

    except IndexError:
        __getName(question)


if __name__ == '__main__':

    #@TODO add custom prefix name into config.cfg file

    #parse arguments provide in command line
    arguments = __parseArguments()

    prefixs = __parsePrefixFromConfig(arguments)


    rootDir = os.path.realpath(arguments.inputFolder)

    #Get the name of the subject
    subjectName = os.path.basename(rootDir)
    if arguments.subjectName:
        subjectName = arguments.subjectName
    answer = raw_input("Please enter a subject name? Defaults {} :".format(subjectName))
    if answer.strip(" ") != "":
        subjectName = answer

    #destination folder



    #  Get the list of subjects folderss
    mriDirs = __listMriDirectories(rootDir)

    map = {}
    map['anat'] = __chooseFolder(mriDirs, "anatomical (T1--MPRAGE)")
    map['dwi'] = __chooseFolder(mriDirs, "diffusion (DTI)")
    map['b0_pa'] = __chooseFolder(mriDirs, "b0 image with posterior to anterior phase-encoding")
    map['b0_ap'] = __chooseFolder(mriDirs, "b0 image with anterior to posterior phase-encoding")

    targetDir = os.path.join(os.getcwd(), "rename_me")
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    for sequence, directory in map.iteritems():

        name = "{}/{}{}".format(targetDir, prefixs[sequence], subjectName)
        if sequence == "dwi":
            cmd = "mrconvert {0} {1}.nii.gz -export_grad_fsl {1}.bvecs {1}.bvals -stride {2}".format(map['dwi'][1], name, "1,2,3,4")
            print cmd
            util.launchCommand(cmd)

            if not arguments.noConfig:
                #determine config.cfg location
                dicoms = glob.glob("{}/*.dcm".format(map['dwi'][1]))
                if len(dicoms) > 0:
                    cmd = "toadinfo {} -c {}/config.cfg".format(dicoms.pop(), targetDir)
                    print cmd
                    util.launchCommand(cmd)
        else:
            cmd = "mrconvert {0} {1}.nii.gz -stride {2}".format(map[sequence][1], name, "1,2,3")
            print cmd
            util.launchCommand(cmd)


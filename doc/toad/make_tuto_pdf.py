#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
print os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
from lib import util

__author__ = "Guillaume Valet"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Guillaume Valet", "Mathieu Desrosiers"]

# Run this script from its own directory
cwd = os.getcwd()
if not 'toad/doc/toad' in cwd:
    print "Please Run this script from its own directory, toad/doc/toad"
    sys.exit()

pandoc = util.which("pandoc")
if pandoc is None:
    print("pandoc not found. Please install the package")
    sys.exit()


# French version
target_dir = 'src/fr/tuto/'
target_file = '../../../Toad_Tuto_fr.pdf' 
header = '../../../head_tuto_fr'
tpl = '../../../../doc_latex.template'
os.chdir(target_dir)
print(os.getcwd())
cmd = "pandoc -s -S %s *.md -o %s --template=%s --number-sections" % (header, target_file, tpl)
print cmd
os.system(cmd)
os.chdir(cwd)
                                                
# English version
target_dir = 'src/en/tuto/'
target_file = '../../../Toad_Tuto_en.pdf' 
header = '../../../head_tuto_en'
tpl = '../../../../doc_latex.template'
os.chdir(target_dir)
print(os.getcwd())
cmd = "pandoc -s -S %s *.md -o %s --template=%s --number-sections" % (header, target_file, tpl)
print cmd
os.system(cmd)

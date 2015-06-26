#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run this script from its own directory

import os

cwd = os.getcwd()

# French version
target_dir = 'src/fr/tuto/'
target_file = '../../../Toad_Tuto_fr.pdf' 
header = '../../../head_tuto_fr'
tpl = '../../../../doc_latex.template'
os.chdir(target_dir)
print(os.getcwd())
os.system("pandoc -s -S %s *.md -o %s --template=%s --number-sections" 
                                                % (header, target_file, tpl))
os.chdir(cwd)
                                                
# English version
target_dir = 'src/en/tuto/'
target_file = '../../../Toad_Tuto_en.pdf' 
header = '../../../head_tuto_en'
tpl = '../../../../doc_latex.template'
os.chdir(target_dir)
print(os.getcwd())
os.system("pandoc -s -S %s *.md -o %s --template=%s --number-sections" 
                                                % (header, target_file, tpl))

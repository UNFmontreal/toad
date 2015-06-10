#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# French version
target_dir = 'src/fr/tuto'
target_file = '../../../Toad_Tuto_fr.pdf' 
header = '../../../head_tuto_fr'
tpl = '../../../../doc_latex.template'
os.chdir(target_dir)
print(os.getcwd())
os.system("pandoc -s -S %s *.md -o %s --template=%s --number-sections" 
                                                % (header, target_file, tpl))

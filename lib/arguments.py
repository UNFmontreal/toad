# -*- coding: utf-8 -*-
import argparse
import sys

__author__ = "Mathieu Desrosiers"
__copyright__ = "Copyright (C) 2014, TOAD"
__credits__ = ["Mathieu Desrosiers"]


class Parser(argparse.ArgumentParser):
    """ override the default behavior of the error method of argument parser

    """
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

import argparse
import sys

class Parser(argparse.ArgumentParser):
    """ override the default behavior of the error method of argument parser

    """
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

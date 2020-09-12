#!/usr/bin/env python

import glob
import os
import shlex
import subprocess
import sys

external_pkg = "ghostscript"


def check_pkg_installed(pkg=external_pkg):
    """Confirms external dependency is install"""
    output = subprocess.run(shlex.split("dpkg -s {}".format(pkg)), capture_output=True)
    pkg_exists = output.returncode == 0
    if pkg_exists:
        return pkg_exists
    else:
        sys.tracebacklimit = 0
        raise SystemError(
            "{0} package is required for PDF compression. "
            'Run "sudo apt install {0}" and then attempt '
            "script run again.".format(pkg)
        )


def list_dirfiles(dirname, ext_type):
    """
    Generates a list of files in a directory that have desired extension
    types as specified.
    :param directory: str pathname of target parent directory
    :param ext_list: list of strings specifying target extension types
        e.g. ['.csv', '.xls']
    :return: list of filenames for files with matching extension type
    """
    filenames = glob.glob("{}/*{}".format(dirname, ext_type))
    n_files = len(filenames)
    return n_files, filenames

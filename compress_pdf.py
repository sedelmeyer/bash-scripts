#!/usr/bin/env python

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

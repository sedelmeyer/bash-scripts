#!/usr/bin/env python
"""
compress_pdf
============

This is a python-based shell script that can be used to compress PDF files in a
Debian-based Linux environment.

To accomplish this, this script invokes the external Ghostscript package. Therefore,
ghostscript is a required dependency or any system in which you run this script.

Otherwise than that external dependency, this script uses only Python standard
libraries. Therefore, no third-party Python libraries are required.

REQUIREMENTS:
    * Debian-based OS
    * ghostscript
    * Python 3.6+

.. note::

   This script will work on other unix-based OS's, however, the
   ``check_pkg_installation`` function will need to be modified to check the appropriate
   package manager for your system (rather than Debian's ``dpkg`` manager)


.. todo::

   The following general steps should be taken to accomplish the desired script behavior

   args and options:

     * source_dir
     * output_dir
     * quality (optional, default is 'printer')
     * --recursive -r
     * --overwrite-files -O
     * --log-results -l

   Requirements backlog, base functionality:

     * Check external package is installed (exit if not)
     * Identify PDF filepaths in source directory
     * Identify and store the number of files and their aggregate size
     * Check for / make output directory
     * Report number of files, original dirname, and output dirname
     * Report size of original files
     * Generate list of output PDF filepaths
     * Iterate through list of PDF files using external package and save to output dir
     * Report and store the size of the outputted files
     * Calculate and report absolute size reduction and compression rate

"""
import glob
import os
import shlex
import subprocess
import sys

external_pkg = "ghostscript"
extension_type = ".pdf"


class PDFCompressor:
    """PDF compression class object"""

    def __init__(
        self, source_dir, output_dir, recursive=False, ext_type=extension_type
    ):
        self.pkg_exists = self.check_pkg_installed(pkg=external_pkg)
        self.source_dir = self.check_source_dir(source_dir=source_dir)
        self.output_dir = self.check_output_dir(output_dir=output_dir)
        self.recursive = recursive
        self.ext_type = ext_type

    def check_pkg_installed(self, pkg):
        """Confirms external dependency is install"""
        output = subprocess.run(
            shlex.split("dpkg -s {}".format(pkg)), capture_output=True
        )
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

    def check_source_dir(self, source_dir):
        """Confirms source_dir exists and raises error if it does not"""
        if not os.path.isdir(source_dir):
            sys.tracebacklimit = 0
            raise ValueError(
                "Invalid source directory value. The following directory does not "
                "exist: {}".format(source_dir)
            )
        else:
            return source_dir

    def check_output_dir(self, output_dir):
        """Confirms output_dir does not already exist, if it does an error is raised"""
        if os.path.isdir(output_dir):
            sys.tracebacklimit = 0
            raise ValueError(
                "Output directory already exists. Please enter the name of the new "
                "directory to which ouput files shall be saved."
            )
        else:
            return output_dir

    def generate_source_dict(self):
        """Walk source_dir to generate dictionary of source directories and files"""
        if self.recursive:
            dir_walk = [(x[0], x[2]) for x in os.walk(self.source_dir)]
            print(dir_walk)
            self.source_dict = {
                dir_name: [
                    os.path.split(filename)[1]
                    for filename in file_list
                    if self.ext_type in filename
                ]
                for (dir_name, file_list) in dir_walk
            }
        else:
            file_list = glob.glob("{}/*{}".format(self.source_dir, self.ext_type))
            self.source_dict = {
                self.source_dir: [
                    os.path.split(filename)[1]
                    for filename in file_list
                    if self.ext_type in filename
                ]
            }

    def list_dirfiles(self, dirname, recursive=True):
        """
        Generates a list of files in a directory that have desired extension
        types as specified.
        :param directory: str pathname of target parent directory
        :param ext_list: list of strings specifying target extension types
            e.g. ['.csv', '.xls']
        :return: list of filenames for files with matching extension type
        """
        filenames = glob.glob(
            "{}/*{}".format(dirname, self.ext_type), recursive=self.recursive
        )
        n_files = len(filenames)
        return n_files, filenames

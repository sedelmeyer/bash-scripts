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
quality_level = "printer"
command_run_external_pkg = (
    "ghostscript -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 "
    "-dPrinted=false -dPDFSETTINGS=/<QUALITY> -dNOPAUSE -dQUIET -dBATCH "
    "-sOutputFile=<OUTPUT> <SOURCE>"
)


class PDFCompressor:
    """PDF compression class object"""

    def __init__(
        self,
        source_dir,
        output_dir,
        output_quality=quality_level,
        recursive=False,
        ext_type=extension_type,
    ):
        self.pkg_exists = self.check_pkg_installed()
        self.source_dir = self.check_source_dir(source_dir=source_dir)
        self.output_dir = self.check_output_dir(output_dir=output_dir)
        self.output_quality = output_quality
        self.recursive = recursive
        self.ext_type = ext_type

    def check_pkg_installed(self):
        """Confirms external dependency is install"""
        command_verify_external_pkg = "dpkg -s {}".format(external_pkg)
        output = subprocess.run(
            shlex.split(command_verify_external_pkg), capture_output=True
        )
        pkg_exists = output.returncode == 0
        if pkg_exists:
            return pkg_exists
        else:
            sys.tracebacklimit = 0
            raise SystemError(
                "{0} package is required for PDF compression. "
                'Run "sudo apt install {0}" and then attempt '
                "script run again.".format(external_pkg)
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
        """Walk source_dir to generate dict of sub-dirs and corresponding files"""
        if self.recursive:
            dir_walk = [(x[0], x[2]) for x in os.walk(self.source_dir)]
            self.source_dict = {
                dir_name: {
                    "files": [
                        os.path.split(filename)[1]
                        for filename in file_list
                        if self.ext_type in filename
                    ]
                }
                for (dir_name, file_list) in dir_walk
            }
        else:
            # if not recursive store only top-level directory and file names
            file_list = glob.glob("{}/*{}".format(self.source_dir, self.ext_type))
            self.source_dict = {
                self.source_dir: {
                    "files": [
                        os.path.split(filename)[1]
                        for filename in file_list
                        if self.ext_type in filename
                    ]
                }
            }

    def generate_output_dict(self):
        """Mirror source_dict to generate output_dict dirs and corresponding files"""
        self.output_dict = {
            key.replace(self.source_dir, self.output_dir): item
            for key, item in self.source_dict.items()
        }

    def generate_dict_metrics(self, source=True):
        """Calculate and add basic count and byte-size metrics to directory dict"""
        # dict_name = "self.{}_dict".format("source" if source else "output")
        dict_name = "{}_dict".format("source" if source else "output")
        directory_dict = getattr(self, dict_name)
        for dirname in directory_dict.keys():
            directory_dict[dirname]["count"] = len(directory_dict[dirname]["files"])
            directory_dict[dirname]["bytes"] = sum(
                [
                    os.stat(os.path.join(dirname, filename)).st_size
                    for filename in directory_dict[dirname]["files"]
                ]
            )
        setattr(self, dict_name, directory_dict)

    def compress_directory_files(self, source_dirname, output_dirname):
        """Compress files for a specific source directory and save to output"""
        output_dirname = self.check_output_dir(output_dirname)
        os.mkdir(output_dirname)

        for filename in self.source_dict[source_dirname]["files"]:
            source_filepath = os.path.join(source_dirname, filename)
            output_filepath = os.path.join(output_dirname, filename)
            subprocess.run(
                shlex.split(
                    command_run_external_pkg.replace("<QUALITY>", self.output_quality)
                    .replace("<OUTPUT>", output_filepath)
                    .replace("<SOURCE>", source_filepath)
                )
            )

import contextlib
import os
import sys
import tempfile
from unittest import TestCase
from unittest import mock

sys.path.append("..")
import compress_pdf  # noqa: E402

source_dirtree = {
    "source": ["test0a.txt", "test0b.not"],
    "source/test00": ["test00a.txt"],
    "source/test01": ["test01a.not"],
    "source/test01/test010": ["test010a.txt"],
}


def build_temp_directories(root_dir, dirtree_dict):
    """Builds a directory structure based on keys in an input dict"""
    dirlist = []
    for dirname in dirtree_dict.keys():
        dirlist.append(os.path.join(root_dir, dirname))
    for dirname in dirlist:
        os.mkdir(dirname)
    return dirlist


def build_temp_files(dirname, filesize_list):
    """Builds source files for use in unittests"""
    raise NotImplementedError


class TestBuildData(TestCase):
    """Test that test data build functions work as expected"""

    def setUp(self):
        with contextlib.ExitStack() as stack:
            # open temp directory context manager
            self.tmpdir = stack.enter_context(tempfile.TemporaryDirectory())
            self.dirlist = build_temp_directories(self.tmpdir, source_dirtree)
            self.addCleanup(stack.pop_all().close)

    def test_build_temp_directories_names(self):
        """Ensure temp directories are named as expected"""
        for dirname_test, dirname in zip(source_dirtree.keys(), self.dirlist):
            self.assertEqual(os.path.join(self.tmpdir, dirname_test), dirname)

    def test_build_temp_directories_exists(self):
        """Ensure temp directories exist after build"""
        for dirname in self.dirlist:
            self.assertTrue(os.path.isdir(dirname))


class TestShrinkFiles(TestCase):
    """Test class functionality"""

    def setUp(self):
        """Set up temporary directory and file structure for tests"""
        with contextlib.ExitStack() as stack:
            # open temp directory context manager
            self.tmpdir = tmpdir = stack.enter_context(tempfile.TemporaryDirectory())
            # set patch for subprocess.run to prevent accidental commands from running
            self.mocked_run = stack.enter_context(
                mock.patch("compress_pdf.subprocess.run")
            )
            self.mocked_run.return_value = self.mocked_run
            self.mocked_run.returncode = 0
            # set source_dir pathname
            self.source_dir = os.path.join(tmpdir, "test0")
            # build nested test/test1/test2/ directory structure in temp directory
            self.dir_list = [self.source_dir]
            self.dir_depth = 3
            for depth in range(1, self.dir_depth):
                self.dir_list.append(
                    os.path.join(self.dir_list[depth - 1], "test{}".format(depth))
                )
            for dirname in self.dir_list:
                os.mkdir(dirname)
            # populate temp directories with test files
            for i, dirname in enumerate(self.dir_list):
                with open(os.path.join(dirname, "test{}.txt".format(i)), "a"):
                    pass
            # set output_dir pathname
            self.output_dir = os.path.join(tmpdir, "test_output")
            # instantiate PDFCompressor object for tests

            self.PDFComp = compress_pdf.PDFCompressor(
                source_dir=self.dir_list[0], output_dir=self.output_dir, ext_type=".txt"
            )
            # reset mock so we can assert calls in test cases
            self.mocked_run.reset_mock()
            # print([x for x in os.walk(tmpdir)])
            # ensure context manager closes after tests
            self.addCleanup(stack.pop_all().close)

    def test_init_pkg_exists(self):
        """Ensure installed package returns ``True``"""
        self.mocked_run.returncode = 0
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, "test")
        self.mocked_run.assert_called_once()
        self.assertTrue(PDFComp.pkg_exists)

    def test_init_pkg_does_not_exist(self):
        """Ensure uninstalled package raises error"""
        self.mocked_run.returncode = 1
        with self.assertRaises(SystemError):
            compress_pdf.PDFCompressor(self.source_dir, "test")
            self.mocked_run.assert_called_once()

    def test_check_source_dir_exists(self):
        """Ensure valid source_dir creates self.source_dir attribute"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, "test")
        self.assertEqual(self.source_dir, PDFComp.source_dir)

    def test_check_source_dir_does_not_exist(self):
        """Ensure invalid source_dir raises ValueError"""
        with self.assertRaises(ValueError):
            compress_pdf.PDFCompressor("test", "test")

    def test_check_output_dir_exists(self):
        """Ensure invalid output_dir creates self.output_dir attribute"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, self.output_dir)
        self.assertEqual(self.output_dir, PDFComp.output_dir)

    def test_check_output_dir_does_not_exist(self):
        """Ensure existing output_dir raises ValueError"""
        with self.assertRaises(ValueError):
            compress_pdf.PDFCompressor(self.source_dir, self.source_dir)

    def test_generate_source_dict_recurse_false(self):
        """Ensure make_dir_list method returns only source_dir when recurse==False"""
        self.PDFComp.generate_source_dict()
        source_dict = self.PDFComp.source_dict
        self.assertEqual(type(source_dict), dict)
        self.assertEqual(len(source_dict), 1)
        self.assertEqual(len(source_dict[self.source_dir]), 1)
        self.assertTrue(self.source_dir in source_dict.keys())

    def test_generate_source_dict_recurse_true(self):
        """Ensure make_dir_list method returns all subdirs when recurse==True"""
        self.PDFComp.recursive = True
        self.PDFComp.generate_source_dict()
        source_dict = self.PDFComp.source_dict
        self.assertEqual(type(source_dict), dict)
        self.assertEqual(len(source_dict), self.dir_depth)
        self.assertListEqual(self.dir_list, list(source_dict.keys()))

    def test_generate_output_dict(self):
        """Ensure generate_output_dict returns mirrored dict"""
        self.PDFComp.recursive = True
        self.PDFComp.generate_source_dict()
        self.PDFComp.generate_output_dict()
        source_dict = self.PDFComp.source_dict
        output_dict = self.PDFComp.output_dict
        self.assertEqual(type(output_dict), dict)
        self.assertEqual(len(source_dict), len(output_dict))
        for key in output_dict.keys():
            self.assertTrue(self.output_dir in key)

    def test_generate_dict_metrics_source(self):
        """Ensure generate_dict_metrics adds counts and bytes to dictionary"""
        self.PDFComp.recursive = True
        self.PDFComp.generate_source_dict()
        self.PDFComp.generate_dict_metrics(source=True)
        source_dict = self.PDFComp.source_dict
        self.assertEqual(type(source_dict), dict)
        self.assertEqual(self.dir_depth, len(source_dict))
        for dir_dict in source_dict.values():
            for dir_metric in dir_dict.keys():
                self.assertIn(dir_metric, ["files", "count", "f_bytes", "d_bytes"])

    def test_format_bytes_value(self):
        """Ensure format_bytes_value formats bytes values correctly"""
        bytes_list = [123, 123e3, 123e6, 123e9]
        bytes_test_list = ["123B", "123K", "123M", "123G"]
        for bytes_value, test_value in zip(bytes_list, bytes_test_list):
            formatted_value = self.PDFComp.format_bytes_value(bytes_value)
            self.assertEqual(formatted_value, test_value)

    @mock.patch("compress_pdf.command_run_external_pkg", "cp <SOURCE> <OUTPUT>")
    def test_run_external_pkg_command(self):
        """Ensure external pkg command runs successfully for all files in directory"""
        self.PDFComp.generate_source_dict()
        self.PDFComp.generate_output_dict()
        self.PDFComp.run_external_pkg_command(self.source_dir, self.output_dir)
        self.assertTrue(os.path.isfile(os.path.join(self.output_dir, "test0.txt")))

    @mock.patch("compress_pdf.command_run_external_pkg", "cp <SOURCE> <OUTPUT>")
    def test_iterate_directories_external_pkg_command(self):
        """Ensure external pkg command runs successfully for all files in directory"""
        self.PDFComp.recursive = True
        self.PDFComp.generate_source_dict()
        self.PDFComp.generate_output_dict()
        self.PDFComp.iterate_directories_external_pkg_command()
        output_files = [x[2][0] for x in os.walk(self.output_dir)]
        source_files = ["test{}.txt".format(i) for i in range(self.dir_depth)]
        self.assertListEqual(output_files, source_files)

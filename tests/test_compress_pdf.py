import contextlib
import os
import sys
import tempfile
from unittest import TestCase
from unittest import mock

sys.path.append("..")
import compress_pdf  # noqa: E402


class TestPDFCompress(TestCase):
    """Test class functionality"""

    @mock.patch("compress_pdf.external_pkg", "nano")
    def setUp(self):
        """Set up temporary directory and file structure for tests"""
        with contextlib.ExitStack() as stack:
            # open temp directory context manager
            self.tmpdir = tmpdir = stack.enter_context(tempfile.TemporaryDirectory())
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
            # print([x for x in os.walk(tmpdir)])
            # ensure context manager closes after tests
            self.addCleanup(stack.pop_all().close)

    @mock.patch("compress_pdf.external_pkg", "nano")
    def test_init_pkg_exists(self):
        """Ensure installed package returns ``True``"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, "test")
        self.assertTrue(PDFComp.pkg_exists)

    @mock.patch("compress_pdf.external_pkg", "sdcfedsawefvvffk")
    def test_init_pkg_does_not_exist(self):
        """Ensure uninstalled package raises error"""
        with self.assertRaises(SystemError):
            compress_pdf.PDFCompressor(self.source_dir, "test")

    @mock.patch("compress_pdf.external_pkg", "nano")
    def test_check_source_dir_exists(self):
        """Ensure valid source_dir creates self.source_dir attribute"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, "test")
        self.assertEqual(self.source_dir, PDFComp.source_dir)

    @mock.patch("compress_pdf.external_pkg", "nano")
    def test_check_source_dir_does_not_exist(self):
        """Ensure invalid source_dir raises ValueError"""
        with self.assertRaises(ValueError):
            compress_pdf.PDFCompressor("test", "test")

    @mock.patch("compress_pdf.external_pkg", "nano")
    def test_check_output_dir_exists(self):
        """Ensure invalid output_dir creates self.output_dir attribute"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, self.output_dir)
        self.assertEqual(self.output_dir, PDFComp.output_dir)

    @mock.patch("compress_pdf.external_pkg", "nano")
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
            self.assertIn("count", dir_dict.keys())
            self.assertIn("bytes", dir_dict.keys())

    @mock.patch("compress_pdf.command_run_external_pkg", "cp <SOURCE> <OUTPUT>")
    def test_compress_directory_files(self):
        """Ensure external pkg command runs successfully for all files in directory"""
        self.PDFComp.generate_source_dict()
        self.PDFComp.generate_output_dict()
        self.PDFComp.compress_directory_files(self.source_dir, self.output_dir)
        self.assertTrue(os.path.isfile(os.path.join(self.output_dir, "test0.txt")))

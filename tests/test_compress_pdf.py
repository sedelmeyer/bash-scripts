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
                source_dir=self.dir_list[0], output_dir=self.output_dir
            )
            print([x for x in os.walk(tmpdir)])
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

    def test_check_source_dir_exists(self):
        """Ensure valid source_dir creates self.source_dir attribute"""
        PDFComp = compress_pdf.PDFCompressor(self.source_dir, "test")
        self.assertEqual(self.source_dir, PDFComp.source_dir)

    def test_check_source_dir_does_not_exist(self):
        """Ensure invalid source_dir raises ValueError"""
        with self.assertRaises(ValueError):
            compress_pdf.PDFCompressor("test", "test")

    def test_make_dir_list_recurse_false(self):
        """Ensure make_dir_list method returns only source_dir when recurse==False"""
        self.PDFComp.make_dir_list()
        dir_list = self.PDFComp.dir_list
        self.assertEqual(len(dir_list), 1)
        self.assertTrue(self.source_dir in dir_list)

    def test_make_dir_list_recurse_true(self):
        """Ensure make_dir_list method returns all subdirs when recurse==True"""
        self.PDFComp.recursive = True
        self.PDFComp.make_dir_list()
        dir_list = self.PDFComp.dir_list
        self.assertEqual(len(dir_list), self.dir_depth)
        self.assertListEqual(self.dir_list, dir_list)

import sys
from unittest import TestCase
from unittest import mock

sys.path.append("..")
import compress_pdf  # noqa: E402


class TestPDFCompress(TestCase):
    """Test class functionality"""

    @mock.patch("compress_pdf.external_pkg", "nano")
    def test_init_pkg_exists(self):
        """Ensure installed package returns ``True``"""
        PDFComp = compress_pdf.PDFCompressor()
        self.assertTrue(PDFComp.pkg_exists)

    @mock.patch("compress_pdf.external_pkg", "sdcfedsawefvvffk")
    def test_init_pkg_does_not_exist(self):
        """Ensure uninstalled package raises error"""
        with self.assertRaises(SystemError):
            compress_pdf.PDFCompressor()

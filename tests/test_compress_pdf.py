import sys
from unittest import TestCase

sys.path.append("..")
import compress_pdf  # noqa: E402


class TestCheckPkg(TestCase):
    """Test ``check_pkg_installed`` function"""

    def test_pkg_exists(self):
        """Ensure installed package returns ``True``"""
        output = compress_pdf.check_pkg_installed(pkg="nano")
        self.assertTrue(output)

    def test_pkg_does_not_exist(self):
        """Ensure uninstalled package raises error"""
        with self.assertRaises(Exception):
            compress_pdf.check_pkg_installed(pkg="fhiesfdlkf")

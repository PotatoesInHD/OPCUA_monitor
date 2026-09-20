import os
import unittest

from exceptions import FatalConfigError
from utils import get_file_path, update_file_path


class TestUtils(unittest.TestCase):
    def test_ok_path(self):
        test1 = get_file_path("", "static_file.txt")
        test2_dir = os.path.abspath("")
        test2_path = os.path.normpath(os.path.join(test2_dir, "static_file.txt"))
        self.assertEqual(test1, test2_path)

    def test_ng_path(self):
        test1 = get_file_path("/bin", "static_file.txt")
        test2_dir = os.path.abspath("")
        test2_path = os.path.normpath(os.path.join(test2_dir, "static_file.txt"))
        self.assertNotEqual(test1, test2_path)

    def test_cfg_error(self):
        with self.assertRaises(FatalConfigError):
            test1 = get_file_path("/bin", "config.ini")

    def test_cfg_error2(self):
        with self.assertRaises(FatalConfigError):
            test1 = get_file_path("", "../main.py")

    def test_update_file_path_ok(self):
        test1 = update_file_path("/1/2/3/4/5.txt", "6.txt")
        test2 = "/1/2/3/4/6.txt"
        self.assertEqual(test1, test2)

    def test_update_file_path_ng(self):
        test1 = update_file_path("/1/2/3/4/5.txt", "6.txt")
        test2 = "/1/2/3/4/5.txt"
        self.assertNotEqual(test1, test2)


if __name__ == "__main__":
    unittest.main()

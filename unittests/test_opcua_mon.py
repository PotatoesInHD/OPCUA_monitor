import os
import datetime
import unittest

from opcua_mon import get_monitored_filename

class TestMonitoredFileName(unittest.TestCase):
    def test_monitor_filename_ok(self):
        pad = "#" if os.name == "nt" else "-"
        date = datetime.datetime.now().astimezone().date()
        monitored_filename = get_monitored_filename()
        test_monitored_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
        self.assertEqual(test_monitored_filename, monitored_filename)


    def test_monitor_filename_ng(self):
        pad = "-" if os.name == "nt" else "#"
        date = datetime.datetime.now().astimezone().date()
        monitored_filename = get_monitored_filename()
        test_monitored_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
        self.assertNotEqual(test_monitored_filename, monitored_filename)


if __name__ == "__main__":
    unittest.main()

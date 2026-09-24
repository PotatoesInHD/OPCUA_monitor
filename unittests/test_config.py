import os
import unittest

from exceptions import FatalConfigError
from config import Config

class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        with open("test_fallbacks_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259

            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1


            [OPCUA_CONFIG]
            #testing empty

            [MONITORED_DIR_PATH]
            #testing empty

            [STATIC_FILE_NAME]
            #testing empty
            """)


        with open("test_minimums_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259

            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1


            [OPCUA_CONFIG]
            SESSION_TIMEOUT = 0
            SOCKET_TIMEOUT = 0
            POLL_SERVER_STATUS_RATE = 0
            HEART_BEAT_INTERVAL = 0
            DELAY_BETWEEN_WRITES = 0
            MAIN_LOOP_DELAY = 0
            """)

        with open("test_maximums_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259

            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1

            [OPCUA_CONFIG]
            SESSION_TIMEOUT = 60_001
            SOCKET_TIMEOUT = 4.1
            POLL_SERVER_STATUS_RATE = 10.1
            HEART_BEAT_INTERVAL = 5.1
            DELAY_BETWEEN_WRITES = 2.1
            MAIN_LOOP_DELAY = 2.1
            """)


        with open("test_exception1_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE =
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259
            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1
            """)


        with open("test_exception2_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE =
            OPCUA_SERVER_STATE = ns=0;i=2259

            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1
            """)

        with open("test_exception3_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE =
            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1
            """)

        with open("test_exception4_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259
            [OPCUA_CLIENT]
            # Example: opc.tcp://192.168.2.199:4840
            OPCUA_URL =
            OPCUA_USERNAME = techweld
            OPCUA_PASSWORD = Robotic1
            """)
        return super().setUp()


    def test_fallbacks_config(self):
        cfg_fallback = Config("test_fallbacks_config.ini")
        # [OPCUA_CONFIG]
        self.assertEqual(cfg_fallback.SESSION_TIMEOUT, 30_000)
        self.assertEqual(cfg_fallback.SOCKET_TIMEOUT, 2)
        self.assertEqual(cfg_fallback.HEART_BEAT_INTERVAL, 3.0)
        self.assertEqual(cfg_fallback.POLL_SERVER_STATUS_RATE, 5.0)
        self.assertEqual(cfg_fallback.DELAY_BETWEEN_WRITES, 0.2)
        self.assertEqual(cfg_fallback.MAIN_LOOP_DELAY, 0.2)
        # [MONITORED_DIR_PATH]
        self.assertEqual(cfg_fallback.MONITORED_DIR_PATH, r"C:\users\user\desktop\servodaata")
        self.assertEqual(cfg_fallback.ENABLE_OPCUA_INFO_LOGS, True)
        # [STATIC_FILE_NAME]
        self.assertEqual(cfg_fallback.STATIC_MONITORED_FILE, "static_file.txt")
        self.assertEqual(cfg_fallback.STATIC_FILE_MODE, False)


    def test_minimums_config(self):
        cfg_min = Config("test_minimums_config.ini")
        # [OPCUA_CONFIG]
        self.assertEqual(cfg_min.SESSION_TIMEOUT, 20_000)
        self.assertEqual(cfg_min.SOCKET_TIMEOUT, 1)
        self.assertEqual(cfg_min.POLL_SERVER_STATUS_RATE, 2.0)
        self.assertEqual(cfg_min.HEART_BEAT_INTERVAL, 1.0)
        self.assertEqual(cfg_min.DELAY_BETWEEN_WRITES, 0.2)
        self.assertEqual(cfg_min.MAIN_LOOP_DELAY, 0.2)


    def test_maximums_config(self):
        cfg_max = Config("test_maximums_config.ini")
        # [OPCUA_CONFIG]
        self.assertEqual(cfg_max.SESSION_TIMEOUT, 60_000)
        self.assertEqual(cfg_max.SOCKET_TIMEOUT, 4)
        self.assertEqual(cfg_max.POLL_SERVER_STATUS_RATE, 10)
        self.assertEqual(cfg_max.HEART_BEAT_INTERVAL, 5)
        self.assertEqual(cfg_max.DELAY_BETWEEN_WRITES, 2)
        self.assertEqual(cfg_max.MAIN_LOOP_DELAY, 2)


    def test_exception1_config(self):
        # [OPCUA_NODE]
        with self.assertRaises(FatalConfigError):
            cfg_exc1 = Config("test_exception1_config.ini")

    def test_exception2_config(self):
        # [OPCUA_NODE]
        with self.assertRaises(FatalConfigError):
            cfg_exc2 = Config("test_exception2_config.ini")

    def test_exception3_config(self):
        # [OPCUA_NODE]
        with self.assertRaises(FatalConfigError):
            cfg_exc3 = Config("test_exception3_config.ini")

    def test_exception4_config(self):
        # [OPCUA_NODE]
        with self.assertRaises(FatalConfigError):
            cfg_exc4 = Config("test_exception4_config.ini")


    def tearDown(self) -> None:
        if os.path.exists("test_fallbacks_config.ini"):
                 os.remove("test_fallbacks_config.ini")
        if os.path.exists("test_minimums_config.ini"):
                os.remove("test_minimums_config.ini")
        if os.path.exists("test_maximums_config.ini"):
                os.remove("test_maximums_config.ini")
        if os.path.exists("test_exception1_config.ini"):
                os.remove("test_exception1_config.ini")
        if os.path.exists("test_exception2_config.ini"):
                os.remove("test_exception2_config.ini")
        if os.path.exists("test_exception3_config.ini"):
                os.remove("test_exception3_config.ini")
        if os.path.exists("test_exception4_config.ini"):
                os.remove("test_exception4_config.ini")
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()

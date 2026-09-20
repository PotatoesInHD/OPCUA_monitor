import os
import unittest

from config import Config

class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        with open("test_config.ini", "w") as f:
            f.write("""
            [OPCUA_NODE]
            TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
            TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
            OPCUA_SERVER_STATE = ns=0;i=2259
            OPCUA_URL = opc.tcp://10.0.0.129:4840
            [OPCUA_CONFIG]
            #testing empty
            [MONITORED_DIR_PATH]
            #testing empty
            [STATIC_FILE_NAME]
            """)
        return super().setUp()

    def test_fallbacks_config(self):
        cfg = Config("test_config.ini")

        assert cfg.SESSION_TIMEOUT == 30_000
        assert cfg.POLL_SERVER_STATUS_RATE == 5.0
        assert cfg.HEART_BEAT_INTERVAL == 3.0
        assert cfg.DELAY_BETWEEN_WRITES == 0.2
        assert cfg.MAIN_LOOP_DELAY == 0.2
        assert cfg.SOCKET_TIMEOUT == 2
        assert cfg.MONITORED_DIR_PATH == r"C:\users\user\desktop\servodaata"
        assert cfg.ENABLE_OPCUA_INFO_LOGS == True
        assert cfg.STATIC_MONITORED_FILE == "static_file.txt"
        assert cfg.STATIC_FILE_MODE == False

   #do after.need to assert exception
   #TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
   #TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
   #OPCUA_SERVER_STATE = ns=0;i=2259
   #OPCUA_URL = opc.tcp://10.0.0.129:4840
   #
    def tearDown(self) -> None:
        if os.path.exists("test_config.ini"):
            return super().tearDown()


if __name__ == "__main__":
    unittest.main()


"""
    [OPCUA_NODE]
    TO_PLC_HEARTBEAT_NODE = ns=1;i=2000
    TO_PLC_FILE_WRITE_DETECTED_NODE = ns=1;i=2002
    OPCUA_SERVER_STATE = ns=0;i=2259
    OPCUA_URL = opc.tcp://10.0.0.129:4840

    [OPCUA_CONFIG]
    SESSION_TIMEOUT =
    SOCKET_TIMEOUT =
    CHECK_SERVER_STATUS_INTERVAL =
    HEART_BEAT_INTERVAL =
    DELAY_BETWEEN_WRITES =
    MAIN_LOOP_DELAY =

    [MONITORED_DIR_PATH]
    MONITORED_DIR_PATH =
    ENABLE_OPCUA_INFO_LOGS =

    [STATIC_FILE_NAME]
    STATIC_MONITORED_FILE =
    STATIC_FILE_MODE =
"""

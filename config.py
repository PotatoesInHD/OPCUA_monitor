import os
import sys
import logging
import configparser
from configparser import NoSectionError, NoOptionError

from utils import get_file_path


logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        # If running compiled inside PyInstaller:
        if getattr(sys, "frozen", False):
            # if running as exe then working directory is where sys.executable is
            working_directory = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # if running as py script then working directory is where script is
            working_directory = os.path.dirname(os.path.abspath(__file__))

        config_path = get_file_path(working_directory, "config.ini")
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")

        try:
            # [OPCUA_NODE]
            self.TO_PLC_HEARTBEAT_NODE = config.get("OPCUA_NODE", "TO_PLC_HEARTBEAT_NODE")
            self.TO_PLC_FILE_WRITE_DETECTED_NODE = config.get("OPCUA_NODE", "TO_PLC_FILE_WRITE_DETECTED_NODE")
            self.OPCUA_SERVER_STATE = config.get("OPCUA_NODE", "OPCUA_SERVER_STATE")
            self.OPCUA_URL = config.get("OPCUA_NODE", "OPCUA_URL")

            # [OPCUA_CONFIG]
            self.SESSION_TIMEOUT = config.getint("OPCUA_CONFIG", "SESSION_TIMEOUT", fallback=30_000)
            self.POLL_SERVER_STATUS_RATE = config.getfloat("OPCUA_CONFIG", "POLL_SERVER_STATUS_RATE", fallback=5.0)
            self.HEART_BEAT_INTERVAL = config.getfloat("OPCUA_CONFIG", "HEART_BEAT_INTERVAL", fallback=3.0)
            self.DELAY_BETWEEN_WRITES = config.getfloat("OPCUA_CONFIG", "DELAY_BETWEEN_WRITES", fallback=0.2)
            self.MAIN_LOOP_DELAY = config.getfloat("OPCUA_CONFIG", "MAIN_LOOP_DELAY", fallback=0.2)
            self.SOCKET_TIMEOUT = config.getfloat("OPCUA_CONFIG", "SOCKET_TIMEOUT", fallback=2)

            # [MDB_DIR_PATH]
            self.MDB_DIR_PATH = config.get("MDB_DIR_PATH", "MDB_DIR_PATH", fallback=r"C:\users\user\desktop\servodaata")

            # [LOG_CONFIG]
            self.ENABLE_OPCUA_INFO_LOGS = config.getboolean("LOG_CONFIG", "ENABLE_OPCUA_INFO_LOGS", fallback=True)

            # Clamps config values
            self.SESSION_TIMEOUT = max(20_000, min(self.SESSION_TIMEOUT, 60_000))
            self.POLL_SERVER_STATUS_RATE = max(2.0, min(self.POLL_SERVER_STATUS_RATE, 10.0))
            self.HEART_BEAT_INTERVAL = max(1.0, min(self.HEART_BEAT_INTERVAL, 5.0))
            self.DELAY_BETWEEN_WRITES = max(0.2, min(self.DELAY_BETWEEN_WRITES, 2.0))
            self.MAIN_LOOP_DELAY = max(0.2, min(self.MAIN_LOOP_DELAY, 2.0))
            self.SOCKET_TIMEOUT = max(1.0, min(self.SOCKET_TIMEOUT, 4.0))

            self.TEST_FILE = config.get("TEST", "TEST_FILE", fallback="test_file.txt")
            self.TEST_MODE = config.getboolean("TEST", "TEST_MODE", fallback=False)


        except (NoSectionError, NoOptionError) as err:
            logger.warning(f"Error: {err}")
            sys.exit(1)
        except Exception as err:
            logger.warning(f"Error: {err}")
            sys.exit(1)

import os
import sys
import configparser

from exceptions import FatalConfigError
from utils import get_file_path


class Config:
    def __init__(self,file_path: str="config.ini"):
        # If running compiled inside PyInstaller:
        if getattr(sys, "frozen", False):
            # if running as exe then working directory is where sys.executable is
            working_directory = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # if running as py script then working directory is where script is
            working_directory = os.path.dirname(os.path.abspath(__file__))

        config_path = get_file_path(working_directory, file_path)
        c = configparser.ConfigParser()
        c.read(config_path, encoding="utf-8")

        # [OPCUA_NODE]
        self.TO_PLC_HEARTBEAT_NODE = c.get("OPCUA_NODE", "TO_PLC_HEARTBEAT_NODE")
        self.TO_PLC_FILE_WRITE_DETECTED_NODE = c.get("OPCUA_NODE", "TO_PLC_FILE_WRITE_DETECTED_NODE")
        self.OPCUA_SERVER_STATE = c.get("OPCUA_NODE", "OPCUA_SERVER_STATE")
        self.OPCUA_URL = c.get("OPCUA_NODE", "OPCUA_URL")

        # [OPCUA_CONFIG]
        self.SESSION_TIMEOUT = c.getint("OPCUA_CONFIG", "SESSION_TIMEOUT", fallback=30_000)
        self.SOCKET_TIMEOUT = c.getfloat("OPCUA_CONFIG", "SOCKET_TIMEOUT", fallback=2)
        self.POLL_SERVER_STATUS_RATE = c.getfloat("OPCUA_CONFIG", "POLL_SERVER_STATUS_RATE", fallback=5.0)
        self.HEART_BEAT_INTERVAL = c.getfloat("OPCUA_CONFIG", "HEART_BEAT_INTERVAL", fallback=3.0)
        self.DELAY_BETWEEN_WRITES = c.getfloat("OPCUA_CONFIG", "DELAY_BETWEEN_WRITES", fallback=0.2)
        self.MAIN_LOOP_DELAY = c.getfloat("OPCUA_CONFIG", "MAIN_LOOP_DELAY", fallback=0.2)

        # [MONITORED_DIR_PATH]
        mon_path_fallback = r"C:\users\user\desktop\servodaata"
        self.MONITORED_DIR_PATH = c.get("MONITORED_DIR_PATH", "MONITORED_DIR_PATH", fallback=mon_path_fallback)

        # [LOG_CONFIG]
        self.ENABLE_OPCUA_INFO_LOGS = c.getboolean("LOG_CONFIG", "ENABLE_OPCUA_INFO_LOGS", fallback=True)

        # [STATIC_FILE_NAME]
        self.STATIC_MONITORED_FILE = c.get("STATIC_FILE_NAME", "STATIC_MONITORED_FILE", fallback="static_file.txt")
        self.STATIC_FILE_MODE = c.getboolean("STATIC_FILE_NAME", "STATIC_FILE_MODE", fallback=False)

        # Clamps config values
        self.SESSION_TIMEOUT = max(20_000, min(self.SESSION_TIMEOUT, 60_000))
        self.SOCKET_TIMEOUT = max(1.0, min(self.SOCKET_TIMEOUT, 4.0))
        self.POLL_SERVER_STATUS_RATE = max(2.0, min(self.POLL_SERVER_STATUS_RATE, 10.0))
        self.HEART_BEAT_INTERVAL = max(1.0, min(self.HEART_BEAT_INTERVAL, 5.0))
        self.DELAY_BETWEEN_WRITES = max(0.2, min(self.DELAY_BETWEEN_WRITES, 2.0))
        self.MAIN_LOOP_DELAY = max(0.2, min(self.MAIN_LOOP_DELAY, 2.0))

        self.TO_PLC_HEARTBEAT_NODE = c.get("OPCUA_NODE", "TO_PLC_HEARTBEAT_NODE")
        self.TO_PLC_FILE_WRITE_DETECTED_NODE = c.get("OPCUA_NODE", "TO_PLC_FILE_WRITE_DETECTED_NODE")
        self.OPCUA_SERVER_STATE = c.get("OPCUA_NODE", "OPCUA_SERVER_STATE")
        self.OPCUA_URL = c.get("OPCUA_NODE", "OPCUA_URL")

        if not self.TO_PLC_HEARTBEAT_NODE:
            raise FatalConfigError(f"Config.ini - TO_PLC_HEARTBEAT_NODE value missing")
        if not self.TO_PLC_FILE_WRITE_DETECTED_NODE:
            raise FatalConfigError(f"Config.ini - TO_PLC_FILE_WRITE_DETECTED_NODE value missing")
        if not self.OPCUA_SERVER_STATE:
            raise FatalConfigError(f"Config.ini - OPCUA_SERVER_STATE value missing")
        if not self.OPCUA_URL:
            raise FatalConfigError(f"Config.ini - OPCUA_URL value missing")

import os
import sys
import logging
import configparser
from configparser import NoSectionError, NoOptionError

from utils import get_file_path


TO_PLC_HEARTBEAT_NODE = "ns=1;i=2000"
TO_PLC_FILE_WRITE_DETECTED_NODE = "ns=1;i=2002"
OPCUA_SERVER_STATE = "ns=0;i=2259"
OPCUA_URL = "opc.tcp://10.0.0.129:4840"
SESSION_TIMEOUT = 30_000  # 30s
MDB_DIR_PATH  = "."
CHECK_SERVER_STATUS_INTERVAL = 5.0 #seconds
DELAY_BETWEEN_WRITES = 0.2 #seconds
HEART_BEAT_INTERVAL = 3.0
MAIN_LOOP_DELAY = 0.2


def setup_config():
    logger = logging.getLogger(__name__)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = get_file_path(BASE_DIR, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")

    try:
        # [OPCUA_NODE]
        TO_PLC_HEARTBEAT_NODE = config.get("OPCUA_NODE", "TO_PLC_HEARTBEAT_NODE")
        TO_PLC_FILE_WRITE_DETECTED_NODE = config.get("OPCUA_NODE", "TO_PLC_FILE_WRITE_DETECTED_NODE")
        OPCUA_SERVER_STATE = config.get("OPCUA_NODE", "OPCUA_SERVER_STATE")
        OPCUA_URL = config.get("OPCUA_NODE", "OPCUA_URL")

        # [OPCUA_CONFIG]
        SESSION_TIMEOUT = config.getint("OPCUA_CONFIG", "SESSION_TIMEOUT", fallback=30_000)
        CHECK_SERVER_STATUS_INTERVAL = config.getfloat("OPCUA_CONFIG", "CHECK_SERVER_STATUS_INTERVAL", fallback=5.0)
        HEART_BEAT_INTERVAL = config.getfloat("OPCUA_CONFIG", "HEART_BEAT_INTERVAL", fallback=3.0)
        DELAY_BETWEEN_WRITES = config.getfloat("OPCUA_CONFIG", "DELAY_BETWEEN_WRITES", fallback=0.2)
        MAIN_LOOP_DELAY = config.getfloat("OPCUA_CONFIG", "MAIN_LOOP_DELAY", fallback=0.2)

        # [MDB_FILE_PATH]
        MDB_DIR_PATH = config.get("MDB_FILE_PATH", "MDB_DIR_PATH", fallback=r"C:\users\user\desktop\servodaata")

    except (NoSectionError, NoOptionError) as err:
        logger.warning(f"Error: {err}")
        sys.exit(1)
    except Exception as err:
        logger.warning(f"Error: {err}")
        sys.exit(1)

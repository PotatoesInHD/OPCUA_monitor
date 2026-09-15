import os
import sys
import time
import logging
import datetime
import threading

from opcua import Client, Node

import config
from config import setup_config
from logger import setup_logger
from utils import get_file_path, FatalConfigError


logger = logging.getLogger(__name__)
# sets up logging from logger.py
setup_logger()

# sets up config from config.py
setup_config()

# lock to prevent threads from read/write at same time
threadlock = threading.Lock()

# -------------background thread-----------
def heartbeat_opcua(node: Node, client: Client, opcua_server_state_node: str, interval: float=3) -> None:
    state = False
    while True:
        state = not state
        opcua_write(node, state)
        time.sleep(interval)
# ------------------------------------------

def opcua_connect(url: str)-> "Client":
        try:
            client = Client(url)
            client.session_timeout = config.SESSION_TIMEOUT
            client.connect()
            return client
        except TimeoutError as err:
            logger.warning(f"Error: {err}...Retrying connection")
        except Exception as err:
            if "BadTooManySessions" in str(err):
                time.sleep(config.SESSION_TIMEOUT / 1000)
            logger.warning(f"Unexpected Error: {err}...Retrying connection")
        time.sleep(5)


def opcua_reconnect(client: Client, opcua_server_state_node: str) -> None:
        opcua_server_state: int | None = opcua_read(opcua_server_state_node)
        if opcua_server_state:
            opcua_disconnect(client)

        while opcua_server_state is None:
            try:
                client.connect()
                opcua_server_state = opcua_read(opcua_server_state_node)
            except TimeoutError as err:
                logger.warning(f"Error: {err}...Retrying connection")
            except Exception as err:
                if "BadTooManySessions" in str(err):
                    time.sleep(config.SESSION_TIMEOUT / 1000)
                logger.warning(f"Unexpected Error: {err}...Retrying connection")
            time.sleep(5)

def opcua_disconnect(client: Client) -> None:
    with threadlock: # prevents both threads from trying to read at same time
        try:
            client.disconnect()
        except Exception as err:
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")
        time.sleep(1)


def opcua_read(node: Node) -> int | None:
    with threadlock: # prevents both threads from trying to read at same time
        try:
            return node.get_value()
        except Exception as err:
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")


def opcua_write(node: Node, value: int | bool) -> None:
    with threadlock: # prevents both threads from trying to write at same time
        try:
            node.set_value(value)
        except Exception as err:
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")
        time.sleep(config.DELAY_BETWEEN_WRITES)


def get_mdb_filename() -> str:
    # "nt" means windows otherwise use "-" this is to remove padding zeros from date
    pad = "#" if os.name == "nt" else "-"
    date = datetime.datetime.now().astimezone().date()
    mdb_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
    return mdb_filename


def close_program(client) -> None:
    if client:
        try:
            client.disconnect()
            sys.exit(130)
        except Exception:
            pass
    os._exit(130)

def main() -> None:
    client: Client | None = None
    try:
        mdb_filename: str = get_mdb_filename()
        # file_path = get_file_path(config.MDB_DIR_PATH, mdb_filename)
        # swap these file_path = later.
        file_path: str = get_file_path(config.MDB_DIR_PATH, "test_file.txt")

        # initialize time variables for monitoring file modified time
        last_modified_time: float = os.stat(file_path).st_mtime
        modified_time: float = last_modified_time

        # Connect to OPCUA server
        while client is None:
            client = opcua_connect(config.OPCUA_URL)

        # load up the nodeid variables
        heartbeat_node: Node = client.get_node(config.TO_PLC_HEARTBEAT_NODE)
        file_write_detected_node: Node = client.get_node(config.TO_PLC_FILE_WRITE_DETECTED_NODE)
        opcua_server_state_node: Node = client.get_node(config.OPCUA_SERVER_STATE)
        # -------Start heartbeat thread in the background------
        heartbeart_thread = threading.Thread(target=heartbeat_opcua, args=(heartbeat_node, client, opcua_server_state_node, config.HEART_BEAT_INTERVAL), daemon=True)
        heartbeart_thread.start()
        # ------------------------------------------------------

        opcua_write(file_write_detected_node, False) #initiliaze write_detect to False
        last_check_status_time = time.monotonic()
        # MainLoop
        while True:
            # get server state and reconnect if required by check status interval time.
            time_now = time.monotonic()
            if (time_now - last_check_status_time) >= config.CHECK_SERVER_STATUS_INTERVAL:
                last_check_status_time = time_now
                opcua_server_state = opcua_read(opcua_server_state_node)
                if opcua_server_state is None:
                    opcua_reconnect(client, opcua_server_state_node)

            # creates mdb database file name based on date.
            mdb_filename = get_mdb_filename()

            modified_time = os.stat(file_path).st_mtime
            if modified_time != last_modified_time:
                last_modified_time = modified_time
                date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
                logger.info(f"File: {mdb_filename}, last modified = {date_st_mtime}")
                opcua_write(file_write_detected_node, True)

            # Main Loop Delay
            time.sleep(config.MAIN_LOOP_DELAY)

    except KeyboardInterrupt:
        close_program(client)

if __name__ == "__main__":
    try:
        main()
    except FatalConfigError:
        # error already logged so exit
        sys.exit(1)
    except Exception:
        logger.exception("Exception caught after main")
        sys.exit(1)

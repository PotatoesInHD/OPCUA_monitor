import os
import sys
import time
import datetime
import threading
import logging
import constants

from logger import setup_logger
import debug_tools

from opcua import Client, Node
# if I decide to read file contents when going to windows will have to
# use pyodbc and Microsoft Access Database Engine
from mdb_parser import MDBParser, MDBTable

threadlock = threading.Lock()   # lock to prevent threads from read/write at same time
# -------------background thread-----------
def heartbeat_opcua(node: Node, interval=3, opcua_server_state_node: str="") -> None:
    state = False
    counter = 0
    while True:
        state = not state
        opcua_write(node, state)
        time.sleep(interval)
# ------------------------------------------

# sets up logging from logger.py
setup_logger()

def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.session_timeout = constants.SESSION_TIMEOUT
        client.connect()
        return client
    except TimeoutError as err:
        logging.warning(f"opcua_connect() - Error: {err}...Retrying connection")
    except Exception as err:
        if "BadTooManySessions" in str(err):
            time.sleep(constants.SESSION_TIMEOUT / 1000)
        logging.warning(f"opcua_connect() - Unexpected Error: {err}...Retrying connection")


def opcua_reconnect(client: Client, opcua_server_state_node: str) -> None:
   opcua_server_state = None
   while opcua_server_state is None:
        time.sleep(5)
        try:
            client.connect()
            opcua_server_state = opcua_read(opcua_server_state_node)
        except TimeoutError as err:
            logging.warning(f"opcua_reconnect() - Error: {err}...Retrying connection")
        except Exception as err:
            if "BadTooManySessions" in str(err):
                time.sleep(constants.SESSION_TIMEOUT / 1000)
            logging.warning(f"opcua_reconnect() - Unexpected Error: {err}...Retrying connection")


def opcua_read(node: Node) -> int | None:
    with threadlock: # prevents both threads from trying to read at same time
        try:
            return node.get_value()
        except Exception as err:
            logging.warning(f"opcua_read() - Error: {err}")

def opcua_write(node: Node, value: int | bool) -> None:
    with threadlock: # prevents both threads from trying to write at same time
        try:
            node.set_value(value)
        except Exception as err:
            logging.warning(f"opcua_write() - Error: {err}")


def get_mdb_filename() -> str:
    # "nt" means windows otherwise use "-"
    pad = "#" if os.name == "nt" else "-"
    date = datetime.date.today()
    mdb_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
    return mdb_filename


def get_file_path(directory: str, file_name: str) -> str:
    #https://pyinstaller.org/en/stable/runtime-information.html
    #look into this when using pyinstaller for determining path of
    # where the exe is can use it to get path to mdb files if in same folder
    try:
        working_dir_abs = os.path.abspath(directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_name))

        valid_target_dir = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        if not valid_target_dir:
            logging.warning(
                f"get_file_path() - Error: Cannot read {file_name} as it is outside"
                f"the permitted working directory"
            )
            return f'Error: Cannot read "{file_name}" as it is outside the permitted working directory'

        target_isfile = os.path.isfile(target_path)
        if not target_isfile:
            logging.warning(f"get_file_path() - Error: {file_name} is not a file")
            return f'Error: "{file_name}" is not a file'

        return target_path
    except Exception as err:
        logging.warning(f"get_file_path() - Error: {err}")
        return f"Error: {err}"


def main() -> None:
    client = None
    try:
        mdb_filename: str = get_mdb_filename()
        # file_path = get_file_path(constants.MDB_DIR_PATH, mdb_filename)
        # swap these file_path = later.
        file_path: str = get_file_path(constants.MDB_DIR_PATH, "test_file.txt")
        #print(file_path, "filepathtest------------------------")

        # initialize time variables for monitoring file modified time
        last_modified_time: float = os.stat(file_path).st_mtime
        modified_time: float = last_modified_time

        # Connect to OPCUA server
        client: Client = None
        while client is None:
            client = opcua_connect(constants.OPCUA_URL)
            time.sleep(5)

        press_write_complete_node = client.get_node(constants.FROM_PLC_WRITE_CMPLT_NODE)
        heartbeat_node = client.get_node(constants.HEARTBEAT_NODE)
        write_detected_node = client.get_node(constants.TO_PLC_WRITE_DETECTED_NODE)
        opcua_server_state_node = client.get_node(constants.OPCUA_SERVER_STATE)

        # -------Start heartbeat thread in the background------
        heartbeart_thread = threading.Thread(target=heartbeat_opcua, args=(heartbeat_node, 3, opcua_server_state_node), daemon=True)
        heartbeart_thread.start()
        # ------------------------------------------------------

        counter = 0
        while True:
            # get server state and reconnect if required
            counter = (counter + 1) % 10
            if counter == 9:
                opcua_server_state = opcua_read(opcua_server_state_node)
                if opcua_server_state is None:
                    opcua_reconnect(client, opcua_server_state_node)

            # creates mdb database file name based on date.
            mdb_filename = get_mdb_filename()

            press_write_complete = opcua_read(press_write_complete_node)

            prev_val = press_write_complete
            modified_time = os.stat(file_path).st_mtime
            if modified_time != last_modified_time:
                last_modified_time = modified_time
                date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
                logging.info(f"File: {mdb_filename}, last modified = {date_st_mtime}")
                opcua_write(write_detected_node, True)

            time.sleep(2)

    except KeyboardInterrupt:
        if client:
            try:
                client.disconnect()
                sys.exit(130)
            except Exception:
                pass
        os._exit(130)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Exception caught after main")
        sys.exit(1)

import os
import time
import datetime
import threading
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from opcua import Client, Node
# if I decide to read file contents when going to windows will have to
# use pyodbc and Microsoft Access Database Engine
from mdb_parser import MDBParser, MDBTable


HEARTBEAT_NODE = "ns=1;i=2003"
WRITE_DETECTED_NODE = "ns=1;i=2002"
FROM_PLC_WRITE_CMPLT_NODE = "ns=1;i=2000"
MDB_DIR_PATH  = "."
OPCUA_URL = "opc.tcp://10.0.0.129:4840"

# background thread
def heartbeat_opcua(node: Node, interval=3.0):
    state = False
    while True:
        try:
            state = not state
            node.set_value(state)
        except Exception as err:
            logging.warning("heartbeat_opcua() - Error: ", err)
        time.sleep(interval)


# setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(message)s')
info_handler = RotatingFileHandler(
    'Info_Logs.log',
    maxBytes=1_000_000,
    backupCount=1,
    encoding='utf-8',
)
# info handler - logs anything less than WARNING
info_handler.setLevel(logging.INFO)
info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
info_handler.setFormatter(formatter)
logger.addHandler(info_handler)

# err handler - logs anything >= WARNING
err_handler = RotatingFileHandler(
    'Error_Logs.log',
    maxBytes=1_000_000,
    backupCount=1,
    encoding='utf-8',
)
err_handler.setFormatter(formatter)
err_handler.addFilter(lambda record: record.levelno >= logging.WARNING)
logger.addHandler(err_handler)


def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.connect()
        logging.warning("Client connected")
        logging.info("Client connected")
        return client
    except TimeoutError as err:
        logging.warning("opcua_connect() - Error: %s...Retrying connection", err)
    except Exception as err:
        logging.warning("opcua_connect() - Unexpected Error: %s...Retrying connection", err)


def opcua_read(node: Node) -> int:
    return node.get_value()


def opcua_write(node: Node, value: int | bool) -> None:
    try:
        node.set_value(value)
    except Exception as err:
        logging.warning("opcua_write() - Error: ",err)


def get_mdb_filename() -> str:
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
            logging.warning("Error: Cannot read %s as it is outside the permitted working directory", file_name)
            return f'Error: Cannot read "{file_name}" as it is outside the permitted working directory'

        target_isfile = os.path.isfile(target_path)
        if not target_isfile:
            logging.warning("Error: %s is not a file", file_name)
            return f'Error: "{file_name}" is not a file'

        return target_path
    except Exception as e:
        logging.warning("get_file_path() - Error: %s", e)
        return f"Error: {e}"


def main() -> None:

    mdb_filename: str = get_mdb_filename()
    # file_path = get_file_path(MDB_DIR_PATH, mdb_filename)
    # swap these file_path = later.
    file_path: str = get_file_path(MDB_DIR_PATH, "test_file.txt")
    #print(file_path, "filepathtest------------------------")

    # initialize time variables
    last_modified_time: float = os.stat(file_path).st_mtime
    modified_time: float = last_modified_time

    client: Client = opcua_connect(OPCUA_URL)
    while client is None:
        client = opcua_connect(OPCUA_URL)
        time.sleep(5)

    press_write_complete_node = client.get_node(FROM_PLC_WRITE_CMPLT_NODE)
    heartbeat_node = client.get_node(HEARTBEAT_NODE)
    # Start heartbeatr thread in the background:
    t = threading.Thread(target=heartbeat_opcua, args=(heartbeat_node, 3.0), daemon=True)
    t.start()

    while True:
        # creates mdb database file name based on date.
        mdb_filename = get_mdb_filename()

        # Sends val 1 to PLC while connected.
        # note for future me - need to make sure this val goes to 0 in plc when disconnected



        press_write_complete = opcua_read(press_write_complete_node)

        modified_time = os.stat(file_path).st_mtime
        if modified_time != last_modified_time:
            last_modified_time = modified_time
            date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
            logging.info("File: %s, last modified = %s", mdb_filename, date_st_mtime)
            #write_detected = client.get_node(WRITE_DETECTED_NODE)
            #opcua_write(write_detected, 1)


        #print(file_path, modified_time)

        time.sleep(2)

        db = MDBParser(file_path="test_mdb.mdb")
        # Get and print the database tables
        ##print(db.tables)
        # Get a table from the DB.
        table = db.get_table("Data")
        # Or you can use the MDBTable class.
        #table = MDBTable(file_path="test_mdb.mdb", table="Data")
        # Get and print the table columns.
        #print(table.columns)
        # Iterate the table rows.
        for row in table:
            break
            print(row[0:11])
            print(len(row))
            break

        # "nt" means windows otherwise use "-"

        #while True:

            #print(str(date)[0:11])
            #print(day_of_week)
            #print(date)
        # print(bs_filename)
            #time.sleep(5)

if __name__ == "__main__":
    main()

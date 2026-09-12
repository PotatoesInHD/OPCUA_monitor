import time
import json
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from opcua import Client
from random import randint, randrange
from mdb_parser import MDBParser, MDBTable

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(message)s')
handler = RotatingFileHandler(
    'Error_Logs.log',
    maxBytes=10000,
    backupCount=1,
    encoding='utf-8',
)

handler.setFormatter(formatter)
logger.addHandler(handler)


# ns=2 Exposed Tags (user-defined)
# i=   Integer
CONN_MONITOR_NODE = "ns=2;i=4"
WRITE_DETECTED_NODE = "ns=2;i=5"
FROM_PLC_WRITE_CMPLT_NODE = "ns=2;i=6"
MDB_DIR_PATH  = "."
OPCUA_URL = "opc.tcp://10.0.0.114:4840"



def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.connect()
        print("Client connected")
        logging.warning("Client connected")
        return client
    except TimeoutError as err:
        print(f"Error: {err}...Retrying connection")
        logging.warning(f"Error: %s...Retrying connection", err)
    except Exception as err:
        print(f"Unexpected Error: {err}...Retrying connection")
        logging.warning(f"Unexpected Error: %s...Retrying connection", err)

def opcua_read(node) -> int:
    return node.get_value()

def opcua_write(node, value: int) -> None:
    node.set_value()

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
            return f'Error: Cannot read "{file_name}" as it is outside the permitted working directory'

        target_isfile = os.path.isfile(target_path)
        if not target_isfile:
            return f'Error: "{file_name}" is not a file'

        return target_path
    except Exception as e:
        return f"Error: {e}"


def main() -> None:

    mdb_filename: str = get_mdb_filename()
    # file_path = get_file_path(MDB_DIR_PATH, mdb_filename)
    # swap these file_path = later.
    file_path: str = get_file_path(MDB_DIR_PATH, "test_file.txt")
    print(file_path, "filepathtest------------------------")

    # initialize time variables
    last_modified_time: float = os.stat(file_path).st_mtime
    modified_time: float = last_modified_time


    client: Client = opcua_connect(OPCUA_URL)
    while client is not None:
        client = opcua_connect(OPCUA_URL)
        time.sleep(5)

    while True:
        # creates mdb database file name based on date.
        mdb_filename = get_mdb_filename()

        # Sends val 1 to PLC while connected.
        # note for future me - need to make sure this val goes to 0 in plc when disconnected
        ###conn_monitor = client.get_node(CONN_MONITOR_NODE)
        ###opcua_write(conn_monitor, 1)

        ###write_complete = opcua_read(FROM_PLC_WRITE_CMPLT_NODE)
        ###if write_complete == 1:
           ### pass
            #write some shenans here for reading file modify time
        modified_time = os.stat(file_path).st_mtime
        if modified_time != last_modified_time:
            last_modified_time = modified_time
            #write_detected = client.get_node(WRITE_DETECTED_NODE)
            #opcua_write(write_detected, 1)


        print(file_path, modified_time)

        time.sleep(2)

        db = MDBParser(file_path="test_mdb.mdb")
        # Get and print the database tables
        print(db.tables)
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

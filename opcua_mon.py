import time
import json
import os
import datetime
from pathlib import Path

from opcua import Client
from random import randint, randrange

# ns=2 Exposed Tags (user-defined)
# i=   Integer
CONN_MONITOR_NODE = "ns=2;i=4"
WRITE_DETECTED_NODE = "ns=2;i=5"
FROM_PLC_WRITE_CMPLT_NODE = "ns=2;i=6"
MDB_DIR_PATH  = "/home/testies/opcuaproj/"
OPCUA_URL = "opc.tcp://10.0.0.114:4840"



def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.connect()
        print("Client connected")
        return client
    except TimeoutError as err:
        print(f"Error: {err}...Retrying connection")
    except Exception as err:
        print(f"Unexpected Error: {err}...Retrying connection")

def opcua_read(node) -> int:
    return node.get_value()

def opcua_write(node, value: int) -> None:
    node.set_value()

def get_mdb_filename() -> str:
    pad = "#" if os.name == "nt" else "-"
    date = datetime.date.today()
    mdb_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
    return mdb_filename


def main() -> None:


    # initialize time variables
    last_modified_time: float = os.stat(MDB_DIR_PATH + "test_file.txt").st_mtime
    modified_time = last_modified_time


    client = opcua_connect(OPCUA_URL)
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
        modified_time = os.stat(MDB_DIR_PATH + "test_file.txt").st_mtime
        if modified_time != last_modified_time:
            last_modified_time = modified_time
            write_detected = client.get_node(WRITE_DETECTED_NODE)
            opcua_write(write_detected, 1)


        print(MDB_DIR_PATH + "test_file.txt", modified_time)

        time.sleep(5)

        # "nt" means windows otherwise use "-"

        #while True:

            #print(str(date)[0:11])
            #print(day_of_week)
            #print(date)
        # print(bs_filename)
            #time.sleep(5)

if __name__ == "__main__":
    main()

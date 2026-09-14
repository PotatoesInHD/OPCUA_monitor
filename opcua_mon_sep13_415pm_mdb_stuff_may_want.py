import os
import time
import datetime
import threading
import logging
from logging.handlers import RotatingFileHandler

from opcua import Client, Node
# if I decide to read file contents when going to windows will have to
# use pyodbc and Microsoft Access Database Engine
from mdb_parser import MDBParser, MDBTable


HEARTBEAT_NODE = "ns=1;i=2003"
WRITE_DETECTED_NODE = "ns=1;i=2002"
FROM_PLC_WRITE_CMPLT_NODE = "ns=1;i=2000"
MDB_DIR_PATH  = "."
OPCUA_URL = "opc.tcp://10.0.0.129:4840"

# -------------background thread-----------
def heartbeat_opcua(node: Node, interval=3.0):
    state = False
    while True:
        try:
            state = not state
            node.set_value(state)
        except Exception as err:
            logging.warning(f"heartbeat_opcua() - Error: {err}")
        time.sleep(interval)
# ------------------------------------------


# setup logging and make "log" directory
working_directory = os.path.abspath(os.getcwd())
target_path = os.path.normpath(os.path.join(working_directory, "logs"))
try:
    os.mkdir(target_path)
except FileExistsError as err:
    pass
except FileNotFoundError as err:
    print(f"Error: {err}")
except Exception as err:
    print(f"Unexpected Error: {err}")

def inspect_filter(record: logging.LogRecord) -> bool: # use to inspect logs
    print(f"Logger: {record.name} | Level: {record.levelname} ({record.levelno}) | Message: {record.getMessage()}")
    return True  # Let it pass through

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(message)s')

# my info handler - logs anything less than WARNING
log_file_path = os.path.normpath(os.path.join(target_path, "Info_Logs.log"))
my_info_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1_000_000,
    backupCount=1,
    encoding='utf-8',
)
my_info_handler.setLevel(logging.INFO)
my_info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
my_info_handler.addFilter(lambda record: "opcua" not in record.name)
# my_info_handler.addFilter(inspect_filter)
my_info_handler.setFormatter(formatter)
logger.addHandler(my_info_handler)

# err handler - logs anything >= WARNING
err_log_file_path = os.path.normpath(os.path.join(target_path, "Error_Logs.log"))
err_handler = RotatingFileHandler(
    err_log_file_path,
    maxBytes=1_000_000,
    backupCount=1,
    encoding='utf-8',
)
err_handler.setFormatter(formatter)
# err_handler.addFilter(inspect_filter)
err_handler.addFilter(lambda record: record.levelno >= logging.WARNING)
logger.addHandler(err_handler)

# opcua info handler - logs anything less than WARNING
opcua_log_file_path = os.path.normpath(os.path.join(target_path, "OPCUA_Info_Logs.log"))
opcua_info_handler = RotatingFileHandler(
    opcua_log_file_path,
    maxBytes=1_000_000,
    backupCount=1,
    encoding='utf-8',
)
opcua_info_handler.setLevel(logging.INFO)
opcua_info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
opcua_info_handler.addFilter(lambda record: "opcua" in record.name)
opcua_info_handler.setFormatter(formatter)
logger.addHandler(opcua_info_handler)

def opcua_connect(url: str)-> "Client":
    try:
        client = Client(url)
        client.connect()
        return client
    except TimeoutError as err:
        logging.warning(f"opcua_connect() - Error: {err}...Retrying connection")
    except Exception as err:
        logging.warning(f"opcua_connect() - Unexpected Error: {err}...Retrying connection")


def opcua_read(node: Node) -> int:
    return node.get_value()


def opcua_write(node: Node, value: int | bool) -> None:
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
            logging.warning(f"Error: Cannot read {file_name} as it is outside the permitted working directory")
            return f'Error: Cannot read "{file_name}" as it is outside the permitted working directory'

        target_isfile = os.path.isfile(target_path)
        if not target_isfile:
            logging.warning(f"Error: {file_name} is not a file")
            return f'Error: "{file_name}" is not a file'

        return target_path
    except Exception as err:
        logging.warning(f"get_file_path() - Error: {err}")
        return f"Error: {err}"


def main() -> None:
    process_time = 0
    last_time = 0
    skip = False
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

    # -------Start heartbeat thread in the background------
    t = threading.Thread(target=heartbeat_opcua, args=(heartbeat_node, 3.0), daemon=True)
    t.start()
    # ------------------------------------------------------

    while True:
        # creates mdb database file name based on date.
        mdb_filename = get_mdb_filename()

        press_write_complete = opcua_read(press_write_complete_node)

        prev_val = press_write_complete
        modified_time = os.stat(file_path).st_mtime
        if modified_time != last_modified_time:
            last_modified_time = modified_time
            date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
            logging.info(f"File: {mdb_filename}, last modified = {date_st_mtime}")
            #write_detected = client.get_node(WRITE_DETECTED_NODE)
            #opcua_write(write_detected, 1)

        #print(file_path, modified_time)

        #time.sleep(0)

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

        #while True:

            #print(str(date)[0:11])
            #print(day_of_week)
            #print(date)
        # print(bs_filename)
            #time.sleep(5)



        if skip == False:
            last_time = time.perf_counter_ns()

        if skip == True:
            process_time = time.perf_counter_ns() - last_time
        print(process_time)
        skip = not skip



if __name__ == "__main__":
    main()

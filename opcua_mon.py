import os
import sys
import time
import logging
import datetime
import threading
from threading import Thread
import tkinter as tk
import cryptography # imported so pyinstaller doesn't complain
from configparser import NoSectionError, NoOptionError

from opcua import Client, Node

from exceptions import FatalConfigError
from config import Config
from logger_cfg import Logger, thread_exception_hook
from utils import get_file_path, update_file_path
from infodisplay import Window, WindowCloseError

#sys.stdout.reconfigure(line_buffering=True) this just for testing. this forces to print right away

logger = logging.getLogger(__name__)

# sets up logging from logger_cfg.py
setup_log = Logger()
log_path = setup_log.setup_logger()

# setup config
try:
    cfg = Config()
except (NoSectionError, NoOptionError) as err:
    logger.warning(f"Error in Config.ini file: {err}", exc_info=True)
    sys.exit(1)
except FatalConfigError as err:
    logger.warning(f"Error: {err}")
    sys.exit(1)
except Exception as err:
    logger.warning(f"Error in Config.ini file: {err}", exc_info=True)
    sys.exit(1)

#updates opcua inf log filter with value from config
setup_log.update_log_filter(cfg.ENABLE_OPCUA_INFO_LOGS)

# overrides threading except hook to capture background thread exceptions and log them
threading.excepthook = thread_exception_hook
# lock to prevent threads from read/write at same time
threadlock = threading.Lock()
# Stop even to tell the background thread when its time to stop so doesn't hang after closing tkinter
stop_event = threading.Event()

#open gui from infodisplay.py
gui = Window(cfg, log_path)


# -------------background thread-----------
def heartbeat_opcua(node: Node, client: Client, opcua_server_state_node: str, interval: float=3) -> None:
    state = False
    while not stop_event.is_set():
        state = not state
        opcua_write(node, state)
        stop_event.wait(timeout=interval)

# ------------------------------------------


def opcua_connect(url: str) -> Client | None:
        client = None
        try:
            client = Client(url, cfg.SOCKET_TIMEOUT)
            client.session_timeout = cfg.SESSION_TIMEOUT
            client.connect()
            return client
        except TimeoutError:
            logger.warning("Time Out Error: ...Retrying connection")
        except OSError as err:
            logger.warning(f"Network Error: {err}...Retrying connection")
        except Exception as err:
            if "BadTooManySessions" in str(err):
                sleep_helper(cfg.SESSION_TIMEOUT / 1000)
            logger.warning(f"Unexpected Error: {err}...Retrying connection")
        sleep_helper(5)


def opcua_reconnect(client: Client, opcua_server_state_node: str) -> None:
        gui.opcua_server_state = opcua_read(opcua_server_state_node)
        if gui.opcua_server_state:
            opcua_disconnect(client)

        while gui.opcua_server_state is None:
            try:
                client.connect()
                gui.opcua_server_state = opcua_read(opcua_server_state_node)
            except TimeoutError:
                logger.warning("Time Out Error: ...Retrying connection")
            except OSError as err:
                logger.warning(f"Network Error: {err}...Retrying connection")
            except Exception as err:
                if "BadTooManySessions" in str(err):
                    sleep_helper(cfg.SESSION_TIMEOUT / 1000)
                logger.warning(f"Unexpected Error: {err}...Retrying connection")
            sleep_helper(5)


def opcua_disconnect(client: Client) -> None:
        try:
            client.disconnect()
        except Exception as err:
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")
        sleep_helper(1)


def opcua_read(node: Node) -> int | None:

    with threadlock: # prevents both threads from trying to read at same time
        try:
            return node.get_value()
        except Exception as err:
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")


def opcua_write(node: Node, value: int | bool) -> None:
    if gui.opcua_server_state:
        with threadlock: # prevents both threads from trying to write at same time
            try:
                node.set_value(value)
            except Exception as err:
                msg = str(err) or str(repr(err)) or "Uknown Error"
                logger.warning(f"Error: {msg}")
            time.sleep(cfg.DELAY_BETWEEN_WRITES)


def get_monitored_filename() -> str:
    # "nt" means windows otherwise use "-" this is to remove padding zeros from date
    pad = "#" if os.name == "nt" else "-"
    date = datetime.datetime.now().astimezone().date()
    monitored_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
    return monitored_filename


class Mtime:
    def __init__(self):
        self.warning_logged_mem = False
    def get_modified_time(self, file_path: str) -> float | None:
        try:
            return os.stat(file_path).st_mtime
            self.warning_logged_mem = False
        except OSError as err:
            if self.warning_logged_mem is False:
                msg = f"Error: {err} - Monitored file at '{file_path}' doesn't exist yet"
                logger.warning(msg)
                logger.info(msg)
                self.warning_logged_mem = True
                print(self.warning_logged_mem)
            return


def close_program(client: Client | None, heartbeat_thread: Thread | None) -> None:
    if heartbeat_thread:
        stop_event.set()
        heartbeat_thread.join(timeout=5)
    if client:
        try:
            client.disconnect()
        except Exception as err:
            logger.warning(f"Error: {err} after program closing")
            os._exit(130)
    sys.exit(130)


def sleep_helper(seconds: float) -> None:
    start_time = time.time()
    while time.time() - start_time < seconds:
        gui.window_update()
        time.sleep(0.05)


def main() -> None:
    heartbeat_thread: Thread | None = None
    modtime = Mtime()
    client: Client | None = None
    try:
        monitored_filename: str = get_monitored_filename()

        if cfg.STATIC_FILE_MODE is False:
            file_path = get_file_path(cfg.MONITORED_DIR_PATH, monitored_filename)
        else:
            file_path: str = get_file_path(cfg.MONITORED_DIR_PATH, cfg.STATIC_MONITORED_FILE)

        gui.file_path = file_path

        # initialize time variables for monitoring file modified time
        last_modified_time: float | None = modtime.get_modified_time(file_path)
        modified_time: float | None = last_modified_time

        # Connect to OPCUA server
        gui.print_console_info()
        while client is None:
            client = opcua_connect(cfg.OPCUA_URL)

        # load up the nodeid variables
        heartbeat_node: Node = client.get_node(cfg.TO_PLC_HEARTBEAT_NODE)
        file_write_detected_node: Node = client.get_node(cfg.TO_PLC_FILE_WRITE_DETECTED_NODE)
        opcua_server_state_node: Node = client.get_node(cfg.OPCUA_SERVER_STATE)

        # -------Start heartbeat thread in the background------
        heartbeat_thread = threading.Thread(
            target=heartbeat_opcua,
            args=(heartbeat_node, client, opcua_server_state_node, cfg.HEART_BEAT_INTERVAL),
            daemon=True
        )

        heartbeat_thread.start()

        # ------------------------------------------------------

        opcua_write(file_write_detected_node, False) #initiliaze write_detect to False
        last_check_status_time = 0
        # MainLoop
        while True:
            # get server state and reconnect if required by check status interval time.
            time_now = time.monotonic()
            if (time_now - last_check_status_time) >= cfg.POLL_SERVER_STATUS_RATE:
                last_check_status_time = time_now
                gui.opcua_server_state = opcua_read(opcua_server_state_node)
                if gui.opcua_server_state is None:
                    gui.window_update()
                    opcua_reconnect(client, opcua_server_state_node)
                gui.window_update()

            # update monitored file name and path
            monitored_filename = get_monitored_filename()
            file_path = update_file_path(file_path, monitored_filename)
            gui.file_path = file_path

            # Monitor the files modified time
            modified_time = modtime.get_modified_time(file_path)
            if modified_time and modified_time != last_modified_time:
                last_modified_time = modified_time
                date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
                logger.info(f"File: {monitored_filename}, last modified = {date_st_mtime}")
                gui.timestamp = str(date_st_mtime)
                opcua_write(file_write_detected_node, True)
            elif last_modified_time:
                gui.timestamp = str(datetime.datetime.fromtimestamp(last_modified_time))

            # Main Loop Delay and GUI update
            gui.window_update()
            sleep_helper(cfg.MAIN_LOOP_DELAY)

    except WindowCloseError as err:
        logger.warning(f"Program closed by user but had WindowCloseError: {err}", exc_info=True)
        close_program(client, heartbeat_thread)
    except (KeyboardInterrupt, tk.TclError):
        logger.warning(f"Program closed by user")
        close_program(client, heartbeat_thread)


if __name__ == "__main__":
    try:
        main()
    except FatalConfigError as err:
        logger.warning(f"Error: {err}")
    except Exception:
        logger.exception("Exception caught after main")
    finally:
        stop_event.set()
        sys.exit(1)

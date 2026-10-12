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

from opcua import Client, Node, ua

from config import Config
from exceptions import FatalConfigError
from infodisplay import Window, WindowCloseError
from utils import get_file_path, update_file_path
from logger_cfg import Logger, thread_exception_hook


logger = logging.getLogger(__name__)
# Global - lock to prevent threads from read/write at same time
threadlock = threading.Lock()
# Global - Stop event to tell the background thread when its time to stop
stop_event = threading.Event()
# Globals - Instances created in main
gui: Window
cfg: Config


class MainPassThrough:
    def __init__(self) -> None:
        # this is to be able to sneak heartbeat_thread outside of main to use thread.join(timeout=#s)
        self.heartbeat_thread: Thread | None = None


def start_heartbeat_thread(heartbeat_node: Node) -> Thread:
    heartbeat_thread = threading.Thread(
        target=heartbeat_opcua,
        args=(heartbeat_node, cfg.HEART_BEAT_INTERVAL),
        daemon=True
    )
    # overrides threading except hook to capture background thread exceptions and log them
    threading.excepthook = thread_exception_hook
    heartbeat_thread.start()
    return heartbeat_thread

# -------------background thread-----------
def heartbeat_opcua(heartbeat_node: Node, interval: float=3) -> None:
    state = False
    while not stop_event.is_set():
        state = not state
        opcua_write(heartbeat_node, state, heartbeat_bg_thread_call=True)
        stop_event.wait(timeout=interval)
# ------------------------------------------

class NodeIds:
    def __init__(self, client: Client) -> None:
        self.heartbeat: Node = client.get_node(cfg.TO_PLC_HEARTBEAT_NODE)
        self.file_write_detected: Node = client.get_node(cfg.TO_PLC_FILE_WRITE_DETECTED_NODE)
        self.opcua_server_state: Node = client.get_node(cfg.OPCUA_SERVER_STATE)


def opcua_connect(client: Client) -> None:
    # Always try to connect until connected and log the errors. PLC wont have heartbeat and alert us
    while True:
        try:
            client.set_user(cfg.OPCUA_USERNAME)
            client.set_password(cfg.OPCUA_PASSWORD)
            client.session_timeout = cfg.SESSION_TIMEOUT
            client.connect()
            return
        except OSError as err:
            logger.warning(f"Error: {err}...Retrying connection")
        except Exception as err:
            if "BadTooManySessions" in str(err):
                sleep_helper(cfg.SESSION_TIMEOUT / 1000)
            logger.warning(f"Unexpected Error: {err}...Retrying connection")
        sleep_helper(5)


def opcua_reconnect(client: Client, opcua_server_state_node: Node) -> None:
    # Always try to reconnect and log the errors. PLC will lose heartbeat and alert us
    opcua_disconnect(client)
    while gui.opcua_server_state is None:
        try:
            client.connect()
            gui.opcua_server_state = opcua_read(opcua_server_state_node)
        except OSError as err:
            logger.warning(f"Error: {err}...Retrying connection")
        except Exception as err:
            if "BadTooManySessions" in str(err):
                sleep_helper(cfg.SESSION_TIMEOUT / 1000)
            logger.warning(f"Unexpected Error: {err}...Retrying connection")
        if not gui.opcua_server_state:
            sleep_helper(5)


def opcua_disconnect(client: Client) -> None:
    try:
        client.disconnect()
    except Exception as err:
        msg = str(err) or str(repr(err)) or "Unknown Error"
        logger.warning(f"Error: {msg}")
    sleep_helper(1)


def opcua_read(node: Node) -> int | str | None:
    with threadlock: # prevents both threads from trying to read at same time
        try:
            return node.get_value()
        except Exception as err:
            # Some of the opcua errors from get_value() were coming out blank. This helped display in logs
            msg = str(err) or str(repr(err)) or "Uknown Error"
            logger.warning(f"Error: {msg}")


def opcua_write(node: Node, value: bool, heartbeat_bg_thread_call: bool=False) -> None:
    if gui.opcua_server_state is not None:
        with threadlock: # prevents both threads from trying to write at same time
            try:
                # data_value format required or sysmac PLC gets angry and gives (BadWriteNotSupported)
                # "The server does not support writing the combination of value, status and timestamps provided."
                data_value = ua.DataValue(ua.Variant(value, node.get_data_type_as_variant_type()))
                node.set_value(data_value)
            except Exception as err:
                msg = str(err) or str(repr(err)) or "Uknown Error"
                logger.warning(f"Error: {msg}")
            # bg heartbeat thread has own delay and Tkinter not threadsafe so cant use sleep_helper() - just return.
            if heartbeat_bg_thread_call:
                return
            sleep_helper(cfg.DELAY_BETWEEN_WRITES)


def poll_server_state(last_check_status_time: float, opcua_server_state: Node) -> float:
    # depending on PLC status may be int or str when connected such as &0 or "run"
    # None is disconnected because opcua server status couldn't be read
    time_now = time.monotonic()
    if (time_now - last_check_status_time) >= cfg.POLL_SERVER_STATUS_RATE:
        last_check_status_time = time_now
        gui.opcua_server_state = opcua_read(opcua_server_state)
        gui.window_update()
    return last_check_status_time


class ModifiedTime:
    def __init__(self) -> None:
        # To prevent filling logs up if new file hasnt been created yet.  Will just log once.
        self.warning_logged_mem = False

    def get_modified_time(self, file_path: str) -> float | None:
        try:
            modified_time = os.stat(file_path).st_mtime
            self.warning_logged_mem = False
            return modified_time
        except OSError as err:
            if self.warning_logged_mem is False:
                msg = f"Error: {err} - Monitored file at '{file_path}' doesn't exist yet"
                logger.warning(msg)
                logger.info(msg)
                self.warning_logged_mem = True
            return


def get_monitored_filename(date: datetime.date | None=None) -> str:
    if cfg.STATIC_FILE_MODE:
        return cfg.STATIC_MONITORED_FILE
    # windows uses "#". "nt" means windows otherwise use "-" this is to remove padding zeros from date
    pad = "#" if os.name == "nt" else "-"
    if not date:
        date = datetime.datetime.now().astimezone().date()
    monitored_filename = date.strftime(f"%{pad}m-%{pad}d-%Y-BS.mdb")
    return monitored_filename


def file_modified_check(modified_time: float | None, last_modified_time: float | None,
    monitored_filename: str) -> tuple[float | None, bool]:
    modified: bool = False
    if modified_time and modified_time != last_modified_time:
        last_modified_time = modified_time
        date_st_mtime = datetime.datetime.fromtimestamp(last_modified_time)
        logger.info(f"File: {monitored_filename}, last modified = {date_st_mtime}")
        gui.timestamp = str(date_st_mtime)
        modified = True
    elif last_modified_time:
        gui.timestamp = str(datetime.datetime.fromtimestamp(last_modified_time))
        modified = False
    return last_modified_time, modified


def close_program(client: Client | None, heartbeat_thread: Thread | None) -> None:
    if heartbeat_thread:
        stop_event.set()
        heartbeat_thread.join(timeout=5)
    if client:
        try:
            client.disconnect()
        except Exception as err:
            logger.warning(f"Error after program closing: {err}")
            # os._exit() or else program often hangs because of open thread from opcua.
            # recreatable if closing program after disconnecting ethernet cable and using sys.exit(130)
            os._exit(130)
    sys.exit(130)


def sleep_helper(seconds: float) -> None:
    # allows sleeping while keeping gui responsive by calling gui.window_update
    start_time = time.monotonic()
    while time.monotonic() - start_time < seconds:
        gui.window_update()
        time.sleep(0.05)


def initialize_logger() -> tuple[str, Logger]:
    log_instance = Logger()
    log_path: str = log_instance.setup_logger()
    return (log_path, log_instance)


def initialize_config():
    global cfg        # setup config, exit if fails
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


def initiliaze_gui(log_path: str, log_instance: Logger) -> None:
    global gui
    gui = Window(cfg, log_path)
    log_instance.setup_gui_handler(gui)


def main(main_pass_through: MainPassThrough) -> None:
    # Initiliazing
    log_path, log_instance = initialize_logger()
    initialize_config()
    log_instance.update_log_filter(cfg.ENABLE_OPCUA_INFO_LOGS)
    initiliaze_gui(log_path, log_instance)
    modtime = ModifiedTime()
    heartbeat_thread: Thread | None = None
    client: Client = Client(cfg.OPCUA_URL, cfg.SOCKET_TIMEOUT)

    try:
        # Get monitored filename and filepath
        monitored_filename: str = get_monitored_filename()
        file_path: str = get_file_path(cfg.MONITORED_DIR_PATH, monitored_filename)
        gui.file_path = file_path

        # initialize time variables for monitoring file modified time
        last_modified_time: float | None = modtime.get_modified_time(file_path)
        modified_time: float | None = last_modified_time

        # Connect to OPCUA server
        gui.print_console_info()
        opcua_connect(client)

        # load up the nodeid variables
        opcua_node = NodeIds(client)

        # -------Start heartbeat thread in the background------
        heartbeat_thread = start_heartbeat_thread(opcua_node.heartbeat)
        main_pass_through.heartbeat_thread = heartbeat_thread
        # ------------------------------------------------------

        opcua_write(opcua_node.file_write_detected, False)  # initiliaze write_detect to False
        last_check_status_time = 0  # initiliaze last check status, so will check on first loop
        # End of Initializing
        # MainLoop
        while True:
            # get server state if required by check status interval time. Then reconnect if needed
            last_check_status_time = poll_server_state(last_check_status_time, opcua_node.opcua_server_state)
            if gui.opcua_server_state is None:
                opcua_reconnect(client, opcua_node.opcua_server_state)

            # Update monitored file name and path if not static mode
            if not cfg.STATIC_FILE_MODE:
                monitored_filename = get_monitored_filename()
                file_path = update_file_path(file_path, monitored_filename)
                gui.file_path = file_path

            # Monitor the files modified time.  If modified then set True. PLC will detect and set back to False.
            modified_time = modtime.get_modified_time(file_path)
            last_modified_time, file_modified = file_modified_check(modified_time, last_modified_time, monitored_filename)
            if file_modified:
                opcua_write(opcua_node.file_write_detected, True)

            # Main Loop Delay and GUI update
            gui.heartbeat_thread_status = heartbeat_thread.is_alive()
            gui.window_update()
            sleep_helper(cfg.MAIN_LOOP_DELAY)

    except WindowCloseError as err:
        logger.warning(f"Program closed by user but had WindowCloseError: {err}", exc_info=True)
        close_program(client, heartbeat_thread)
    except (KeyboardInterrupt, tk.TclError):
        logger.warning(f"Program closed by user")
        close_program(client, heartbeat_thread)


if __name__ == "__main__":
    main_pass_through = MainPassThrough()
    try:
        main(main_pass_through)
    except FatalConfigError as err:
        logger.warning(f"Error: {err}")
    except Exception:
        logger.exception("Exception caught after main")
    finally:
        stop_event.set()
        if main_pass_through.heartbeat_thread:
            main_pass_through.heartbeat_thread.join(timeout=5)
        sys.exit(1)

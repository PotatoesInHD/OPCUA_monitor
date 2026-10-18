import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from infodisplay import Window


logger = logging.getLogger(__name__)


def make_dir_target_path() -> str:
    # if running compiled inside PyInstaller:
    if getattr(sys, "frozen", False):
        # if running as exe then working directory is where sys.executable is
        working_directory = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # if running as py script then working directory is where script is
        working_directory = os.path.dirname(os.path.abspath(__file__))

    target_path = os.path.normpath(os.path.join(working_directory, "logs"))
    os.makedirs(target_path, exist_ok=True)
    return target_path


def setup_info_handler(info_formatter: logging.Formatter, target_path: str) -> RotatingFileHandler:
    # my info handler - logs anything less than WARNING
    info_log_file_path = os.path.normpath(os.path.join(target_path, "Info_Logs.log"))
    info_handler = RotatingFileHandler(
        info_log_file_path,
        maxBytes=10_000_000,
        backupCount=1,
        encoding='utf-8',
    )
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    # filters all the logs from opcua modules as they have their own handler and log file
    info_handler.addFilter(lambda record: "opcua" not in record.name)
    info_handler.setFormatter(info_formatter)
    return info_handler


def setup_err_handler(err_formatter: logging.Formatter, target_path: str) -> RotatingFileHandler:
    # err handler - logs anything >= WARNING
    err_log_file_path = os.path.normpath(os.path.join(target_path, "Error_Logs.log"))
    err_handler = RotatingFileHandler(
        err_log_file_path,
        maxBytes=10_000_000,
        backupCount=1,
        encoding='utf-8',
    )
    err_handler.setFormatter(err_formatter)
    err_handler.addFilter(lambda record: record.levelno >= logging.WARNING)
    return err_handler


def setup_opcua_info_handler(info_formatter: logging.Formatter, target_path: str) -> RotatingFileHandler:
    # opcua info handler - logs anything less than WARNING - can be enabled/disabled
    opcua_log_file_path = os.path.normpath(os.path.join(target_path, "OPCUA_Info_Logs.log"))
    opcua_info_handler = RotatingFileHandler(
        opcua_log_file_path,
        maxBytes=10_000_000,
        backupCount=1,
        encoding='utf-8',
    )
    opcua_info_handler.setLevel(logging.INFO)
    opcua_info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    opcua_info_handler.setFormatter(info_formatter)
    return opcua_info_handler


class GuiErrorHandler(logging.Handler):
    def __init__(self, gui: Window) -> None:
        super().__init__()
        self.gui = gui
    # override emit method to get last error for gui
    def emit(self, record: logging.LogRecord) -> None:
        self.gui.last_error = self.format(record)


class Logger:
    def __init__(self) -> None:
        # opcua info handler instance variable so handler can be setup and then filter updated later in other method
        self.opcua_info_handler: RotatingFileHandler

    def setup_logger(self) -> str:
        # make logs directory and return the target path
        target_path = make_dir_target_path()

        # setup root logger and formatters
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d in %(funcName)s()] - %(message)s'
        err_formatter = logging.Formatter(fmt_str)

        # setup info handler
        info_handler = setup_info_handler(info_formatter, target_path)
        self.logger.addHandler(info_handler)
        # setup err handler
        err_handler = setup_err_handler(err_formatter, target_path)
        self.logger.addHandler(err_handler)
        # setup opcua info handler
        self.opcua_info_handler = setup_opcua_info_handler(info_formatter, target_path)
        self.logger.addHandler(self.opcua_info_handler)
        return target_path

    def update_log_filter(self, enable_opcua_info_logs: bool) -> None:
        self.opcua_info_handler.addFilter(lambda record: enable_opcua_info_logs and "opcua" in record.name)

    def setup_gui_handler(self, gui: Window) -> None:
        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d in %(funcName)s()] - %(message)s'
        gui_formatter = logging.Formatter(fmt_str)
        self.gui_handler = GuiErrorHandler(gui)
        self.gui_handler.setLevel(logging.WARNING)
        self.gui_handler.setFormatter(gui_formatter)
        self.logger.addHandler(self.gui_handler)


def thread_exception_hook(args) -> None:
    logger.error(
        f"Background thread crash in {args.thread.name}",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )

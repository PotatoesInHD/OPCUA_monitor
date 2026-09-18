import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler


logger = logging.getLogger(__name__)


class Logger:
    def __init__(self) -> None:
        self.opcua_info_handler: RotatingFileHandler

    def setup_logger(self) -> str:

        # If running compiled inside PyInstaller:
        if getattr(sys, "frozen", False):
            # if running as exe then working directory is where sys.executable is
            working_directory = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # if running as py script then working directory is where script is
            working_directory = os.path.dirname(os.path.abspath(__file__))

        target_path = os.path.normpath(os.path.join(working_directory, "logs"))
        os.makedirs(target_path, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        err_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - [%(filename)s:%(lineno)d in %(funcName)s()] - %(message)s')
        # my info handler - logs anything less than WARNING
        log_file_path = os.path.normpath(os.path.join(target_path, "Info_Logs.log"))
        my_info_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=10_000_000,
            backupCount=1,
            encoding='utf-8',
        )
        my_info_handler.setLevel(logging.INFO)
        my_info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        my_info_handler.addFilter(lambda record: "opcua" not in record.name)
        my_info_handler.setFormatter(info_formatter)
        logger.addHandler(my_info_handler)

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
        logger.addHandler(err_handler)

        # opcua info handler - logs anything less than WARNING - can be enabled/disabled
        opcua_log_file_path = os.path.normpath(os.path.join(target_path, "OPCUA_Info_Logs.log"))
        self.opcua_info_handler = RotatingFileHandler(
            opcua_log_file_path,
            maxBytes=10_000_000,
            backupCount=1,
            encoding='utf-8',
        )
        self.opcua_info_handler.setLevel(logging.INFO)
        self.opcua_info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
        self.opcua_info_handler.setFormatter(info_formatter)
        logger.addHandler(self.opcua_info_handler)

        return target_path

    def update_log_filter(self, enable_opcua_info_logs: bool) ->None:
        self.opcua_info_handler.addFilter(lambda record: enable_opcua_info_logs and "opcua" in record.name)


def thread_exception_hook(args) -> None:
    if issubclass(args.exc_type, (AttributeError, OSError)):
        logger.warning(f"Error: {args.thread.name} - {args.exc_type} - {args.exc_value}")
        return
    logger.error(
        f"Background thread crash in {args.thread.name}",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )

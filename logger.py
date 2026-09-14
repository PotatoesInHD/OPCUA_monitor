import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
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

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(message)s')

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
    # my_info_handler.addFilter(inspect_filter)
    my_info_handler.setFormatter(formatter)
    logger.addHandler(my_info_handler)

    # err handler - logs anything >= WARNING
    err_log_file_path = os.path.normpath(os.path.join(target_path, "Error_Logs.log"))
    err_handler = RotatingFileHandler(
        err_log_file_path,
        maxBytes=10_000_000,
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

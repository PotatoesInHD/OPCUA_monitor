import os
import logging
from exceptions import FatalConfigError



def get_file_path(directory: str, file_name: str) -> str:
    working_dir_abs = os.path.abspath(directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_name))
    valid_target_dir = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs

    if not valid_target_dir:
        msg = (
            f"Cannot read {file_name} as it is outside"
            f"the permitted working directory"
        )
        raise FatalConfigError(msg)

    target_isfile = os.path.isfile(target_path)
    if not target_isfile and file_name == "config.ini":
        msg = f"Config.ini File Missing. Config.ini file must stay in same directory as opcua_mon.py/exe"
        raise FatalConfigError(msg)
    return target_path

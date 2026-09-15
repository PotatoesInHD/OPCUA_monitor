import os
import logging

logger = logging.getLogger(__name__)


class FatalConfigError(Exception):
    """Raised when config data is missing. Such as file path"""


def get_file_path(directory: str, file_name: str) -> str:
    working_dir_abs = os.path.abspath(directory)
    target_path = os.path.normpath(os.path.join(working_dir_abs, file_name))
    valid_target_dir = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs

    if not valid_target_dir:
        msg = (
            f"Error: Cannot read {file_name} as it is outside"
            f"the permitted working directory"
        )
        logger.warning(msg)
        raise FatalConfigError(msg)

    target_isfile = os.path.isfile(target_path)
    if not target_isfile:
        msg = f"Error: {file_name} is not a file"
        logger.warning(msg)
        raise FatalConfigError(msg)
    return target_path





class FatalConfigError(Exception):
    """Raised when config data is missing. Such as file path"""

class WindowCloseError(Exception):
        """Raised when gui window closes but doesnt give tk.tclerror"""

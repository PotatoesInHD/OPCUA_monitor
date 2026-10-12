
# Custom Exceptions
class FatalConfigError(Exception):
    pass # Raised when config data is missing. Such as file path


class WindowCloseError(Exception):
    pass # Raised when gui window closes but doesnt give tk.TclError
